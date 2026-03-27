"""
finetune_vocoder.py — Svara-Chanda Dev 3 (Neural Audio Engineer)
Fine-tune HiFi-GAN vocoder on Sanskrit speech corpus.

Usage:
    python finetune_vocoder.py --corpus_dir backend/data/audio/sanskrit_speech_corpus \
                                --epochs 10 --lr 2e-4 --batch_size 8

Requires: torch, torchaudio, soundfile, numpy
Falls back gracefully if torch is not installed (Python 3.14 incompatibility).
"""

import argparse
import logging
import os
import sys
import time
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("finetune_vocoder")

# ---------------------------------------------------------------------------
# Torch guard — fail cleanly on Python 3.14 where torch isn't available
# ---------------------------------------------------------------------------
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import Dataset, DataLoader
    import numpy as np
    import soundfile as sf
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


# ---------------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------------

class SanskritSpeechDataset:
    """
    Loads WAV + text pairs from a corpus directory.

    Expected corpus layout:
        corpus_dir/
            metadata.csv        # format: filename|transcription
            wavs/
                file001.wav
                file002.wav
                ...

    Falls back to scanning all .wav files if metadata.csv is absent.
    """

    def __init__(self, corpus_dir: str, sample_rate: int = 22050, max_duration_sec: float = 10.0):
        if not TORCH_AVAILABLE:
            raise RuntimeError("torch is required for SanskritSpeechDataset")

        self.corpus_dir = Path(corpus_dir)
        self.sample_rate = sample_rate
        self.max_samples = int(max_duration_sec * sample_rate)
        self.items = self._load_manifest()
        logger.info("Dataset loaded: %d items from %s", len(self.items), corpus_dir)

    def _load_manifest(self):
        metadata_path = self.corpus_dir / "metadata.csv"
        wav_dir = self.corpus_dir / "wavs"

        items = []
        if metadata_path.exists():
            with open(metadata_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    parts = line.split("|", 1)
                    if len(parts) == 2:
                        fname, text = parts
                        wav_path = wav_dir / fname if not fname.endswith(".wav") else wav_dir / fname
                        if not wav_path.suffix:
                            wav_path = wav_path.with_suffix(".wav")
                        if wav_path.exists():
                            items.append({"wav": str(wav_path), "text": text})
        else:
            # Fallback: scan all .wav files, use filename as pseudo-transcription
            search_dir = wav_dir if wav_dir.exists() else self.corpus_dir
            for wav_path in sorted(search_dir.glob("**/*.wav")):
                items.append({"wav": str(wav_path), "text": wav_path.stem})

        if not items:
            raise FileNotFoundError(
                f"No WAV files found in {self.corpus_dir}. "
                "Ensure corpus_dir contains wavs/ subdirectory or .wav files."
            )
        return items

    def __len__(self):
        return len(self.items)

    def __getitem__(self, idx):
        item = self.items[idx]
        audio, sr = sf.read(item["wav"], dtype="float32")

        # Resample if needed (simple nearest-neighbour; use torchaudio.transforms for quality)
        if sr != self.sample_rate:
            import torchaudio
            waveform = torch.from_numpy(audio).unsqueeze(0)
            resampler = torchaudio.transforms.Resample(orig_freq=sr, new_freq=self.sample_rate)
            audio = resampler(waveform).squeeze(0).numpy()

        # Mono
        if audio.ndim > 1:
            audio = audio.mean(axis=1)

        # Pad or truncate
        if len(audio) > self.max_samples:
            audio = audio[: self.max_samples]
        else:
            audio = np.pad(audio, (0, self.max_samples - len(audio)))

        return torch.tensor(audio, dtype=torch.float32)


def collate_fn(batch):
    """Stack waveforms into a (B, T) tensor."""
    return torch.stack(batch)


# ---------------------------------------------------------------------------
# Minimal HiFi-GAN stand-in
# (Replace with real HiFi-GAN checkpoint loading for production)
# ---------------------------------------------------------------------------

if TORCH_AVAILABLE:
    class MinimalVocoderModel(nn.Module):
        """
        Lightweight 1-D CNN vocoder proxy.
    
        In production, replace this with:
            from hifigan.models import Generator
            model = Generator(h)
            model.load_state_dict(torch.load(checkpoint_path)['generator'])
    
        This stand-in is sufficient for fine-tuning pipeline validation
        when a real HiFi-GAN checkpoint is unavailable.
        """
    
        def __init__(self, in_channels: int = 1, hidden: int = 64):
            super().__init__()
            self.net = nn.Sequential(
                nn.Conv1d(in_channels, hidden, kernel_size=7, padding=3),
                nn.LeakyReLU(0.1),
                nn.Conv1d(hidden, hidden, kernel_size=5, padding=2),
                nn.LeakyReLU(0.1),
                nn.Conv1d(hidden, in_channels, kernel_size=3, padding=1),
                nn.Tanh(),
            )
    
        def forward(self, x: torch.Tensor) -> torch.Tensor:
            # x: (B, T) → (B, 1, T) → (B, T)
            return self.net(x.unsqueeze(1)).squeeze(1)
    
    
    # ---------------------------------------------------------------------------
    # Training loop
    # ---------------------------------------------------------------------------
    
def train(args):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info("Training device: %s", device)

    # Dataset & DataLoader
    dataset = SanskritSpeechDataset(
        corpus_dir=args.corpus_dir,
        sample_rate=22050,
    )
    dataloader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=0,          # Keep 0 for hackathon stability
        drop_last=len(dataset) >= args.batch_size,
        collate_fn=collate_fn,
    )

    # Model
    model = MinimalVocoderModel().to(device)
    optimizer = optim.Adam(model.parameters(), lr=args.lr)
    loss_fn = nn.L1Loss()

    # Optional wandb
    use_wandb = False
    if args.wandb:
        try:
            import wandb
            wandb.init(project="svara-chanda", name="finetune-vocoder", config=vars(args))
            use_wandb = True
            logger.info("wandb logging enabled")
        except ImportError:
            logger.warning("wandb not installed — skipping wandb logging")

    # Checkpoint output dir
    checkpoint_dir = Path("backend/data/models/vocoder")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    # Early stopping state
    best_val_loss = float("inf")
    no_improve_epochs = 0
    PATIENCE = 3

    logger.info("Starting fine-tuning: %d epochs, lr=%.2e, batch_size=%d",
                args.epochs, args.lr, args.batch_size)

    for epoch in range(1, args.epochs + 1):
        model.train()
        epoch_loss = 0.0
        t0 = time.time()

        for batch in dataloader:
            batch = batch.to(device)
            optimizer.zero_grad()
            output = model(batch)
            loss = loss_fn(output, batch)   # Reconstruction loss
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            epoch_loss += loss.item()

        avg_loss = epoch_loss / max(len(dataloader), 1)
        elapsed = time.time() - t0
        logger.info("Epoch %d/%d — loss: %.6f — time: %.1fs", epoch, args.epochs, avg_loss, elapsed)

        if use_wandb:
            import wandb
            wandb.log({"epoch": epoch, "train_loss": avg_loss})

        # Save checkpoint every epoch
        ckpt_path = checkpoint_dir / f"ft_{epoch}.pt"
        torch.save({
            "epoch": epoch,
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "loss": avg_loss,
        }, ckpt_path)
        logger.info("Checkpoint saved → %s", ckpt_path)

        # Early stopping (using train loss as proxy; swap for val loss if you add a val split)
        if avg_loss < best_val_loss:
            best_val_loss = avg_loss
            no_improve_epochs = 0
            # Save best model separately
            torch.save(model.state_dict(), checkpoint_dir / "ft_best.pt")
            logger.info("New best model saved → ft_best.pt")
        else:
            no_improve_epochs += 1
            logger.info("No improvement for %d/%d patience epochs", no_improve_epochs, PATIENCE)
            if no_improve_epochs >= PATIENCE:
                logger.info("Early stopping triggered at epoch %d", epoch)
                break

    logger.info("Fine-tuning complete. Best loss: %.6f", best_val_loss)
    if use_wandb:
        import wandb
        wandb.finish()


# ---------------------------------------------------------------------------
# Demo mode — runs without torch, generates a placeholder checkpoint file
# ---------------------------------------------------------------------------

def demo_mode(args):
    """
    Dry-run for Python 3.14 / no-torch environments.
    Validates corpus path, logs what *would* happen, saves a dummy manifest.
    """
    logger.warning("torch not available — running in DEMO MODE (no actual training)")
    corpus_dir = Path(args.corpus_dir)

    if not corpus_dir.exists():
        logger.warning("Corpus dir '%s' does not exist — creating stub structure", corpus_dir)
        (corpus_dir / "wavs").mkdir(parents=True, exist_ok=True)
        (corpus_dir / "metadata.csv").write_text(
            "# filename|transcription\n"
            "# example001|namaH zivAya\n",
            encoding="utf-8",
        )
        logger.info("Created stub corpus at %s", corpus_dir)

    ckpt_dir = Path("backend/data/models/vocoder")
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    demo_ckpt = ckpt_dir / "ft_demo.json"
    import json
    demo_ckpt.write_text(json.dumps({
        "mode": "demo",
        "epochs_planned": args.epochs,
        "lr": args.lr,
        "batch_size": args.batch_size,
        "note": "Real training requires torch. Install via: pip install torch torchaudio"
    }, indent=2))
    logger.info("Demo manifest saved → %s", demo_ckpt)
    logger.info("Pipeline structure validated. Ready for torch when available.")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Fine-tune HiFi-GAN vocoder on Sanskrit speech corpus (Svara-Chanda Dev 3)"
    )
    parser.add_argument(
        "--corpus_dir",
        default="backend/data/audio/sanskrit_speech_corpus",
        help="Path to corpus directory (contains wavs/ and metadata.csv)",
    )
    parser.add_argument("--epochs", type=int, default=10, help="Number of training epochs")
    parser.add_argument("--lr", type=float, default=2e-4, help="Learning rate")
    parser.add_argument("--batch_size", type=int, default=8, help="Batch size")
    parser.add_argument(
        "--wandb", action="store_true", help="Enable wandb logging if available"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if not TORCH_AVAILABLE:
        demo_mode(args)
        sys.exit(0)

    try:
        train(args)
    except FileNotFoundError as e:
        logger.error("Corpus not found: %s", e)
        logger.info("Tip: Place WAV files in %s/wavs/ and create metadata.csv", args.corpus_dir)
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Training interrupted by user")
        sys.exit(0)
