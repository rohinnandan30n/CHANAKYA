import { describe, it, expect } from 'vitest';

describe('Mantra Data Validation', () => {
  const MANTRAS = [
    {
      text: 'ॐ',
      meaning: 'Om',
      translation: 'The primordial sound of the universe',
      color: 0xa85c2a,
      significance: 'Represents the ultimate reality and consciousness. The foundation of all mantras.',
    },
    {
      text: 'नमस्ते',
      meaning: 'Namaste',
      translation: 'I bow to you',
      color: 0xd97706,
      significance: 'Expression of respect and recognition of the divine within others.',
    },
    {
      text: 'शान्तिः',
      meaning: 'Shanti',
      translation: 'Peace',
      color: 0xf59e0b,
      significance: 'Invocation of peace in body, mind, and spirit. Often chanted three times.',
    },
    {
      text: 'सत्यम्',
      meaning: 'Satya',
      translation: 'Truth',
      color: 0xfbbf24,
      significance: 'Represents absolute truth and the pursuit of knowledge and wisdom.',
    },
  ];

  it('should have exactly 4 mantras', () => {
    expect(MANTRAS).toHaveLength(4);
  });

  it('should have correct structure for each mantra', () => {
    MANTRAS.forEach((mantra) => {
      expect(mantra).toHaveProperty('text');
      expect(mantra).toHaveProperty('meaning');
      expect(mantra).toHaveProperty('translation');
      expect(mantra).toHaveProperty('color');
      expect(mantra).toHaveProperty('significance');
    });
  });

  it('should have valid Sanskrit text for each mantra', () => {
    const validTexts = ['ॐ', 'नमस्ते', 'शान्तिः', 'सत्यम्'];
    MANTRAS.forEach((mantra, index) => {
      expect(mantra.text).toBe(validTexts[index]);
    });
  });

  it('should have non-empty meanings', () => {
    MANTRAS.forEach((mantra) => {
      expect(mantra.meaning.length).toBeGreaterThan(0);
      expect(mantra.meaning).toBeTruthy();
    });
  });

  it('should have non-empty translations', () => {
    MANTRAS.forEach((mantra) => {
      expect(mantra.translation.length).toBeGreaterThan(0);
      expect(mantra.translation).toBeTruthy();
    });
  });

  it('should have non-empty significance descriptions', () => {
    MANTRAS.forEach((mantra) => {
      expect(mantra.significance.length).toBeGreaterThan(0);
      expect(mantra.significance).toBeTruthy();
    });
  });

  it('should have valid hex color codes', () => {
    const validColors = [0xa85c2a, 0xd97706, 0xf59e0b, 0xfbbf24];
    MANTRAS.forEach((mantra, index) => {
      expect(mantra.color).toBe(validColors[index]);
      expect(mantra.color).toBeGreaterThan(0);
      expect(mantra.color).toBeLessThanOrEqual(0xffffff);
    });
  });

  it('should have unique mantra texts', () => {
    const texts = MANTRAS.map((m) => m.text);
    const uniqueTexts = new Set(texts);
    expect(uniqueTexts.size).toBe(MANTRAS.length);
  });

  it('should have unique meanings', () => {
    const meanings = MANTRAS.map((m) => m.meaning);
    const uniqueMeanings = new Set(meanings);
    expect(uniqueMeanings.size).toBe(MANTRAS.length);
  });

  it('should have proper string types for all text fields', () => {
    MANTRAS.forEach((mantra) => {
      expect(typeof mantra.text).toBe('string');
      expect(typeof mantra.meaning).toBe('string');
      expect(typeof mantra.translation).toBe('string');
      expect(typeof mantra.significance).toBe('string');
    });
  });

  it('should have proper number type for color', () => {
    MANTRAS.forEach((mantra) => {
      expect(typeof mantra.color).toBe('number');
    });
  });

  it('should have meaningful significance descriptions', () => {
    MANTRAS.forEach((mantra) => {
      expect(mantra.significance.length).toBeGreaterThan(20);
    });
  });
});
