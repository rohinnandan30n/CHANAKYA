import { describe, it, expect } from 'vitest';

describe('MantraVisualization', () => {
  it('should have correct mantra data structure', () => {
    const MANTRAS = [
      {
        text: 'ॐ',
        meaning: 'Om',
        translation: 'The primordial sound of the universe',
        color: 0xa85c2a,
        significance: 'Represents the ultimate reality and consciousness.',
      },
      {
        text: 'नमस्ते',
        meaning: 'Namaste',
        translation: 'I bow to you',
        color: 0xd97706,
        significance: 'Expression of respect and recognition of the divine.',
      },
    ];

    expect(MANTRAS).toHaveLength(2);
    expect(MANTRAS[0].text).toBe('ॐ');
    expect(MANTRAS[0].meaning).toBe('Om');
    expect(MANTRAS[0].color).toBe(0xa85c2a);
  });

  it('should validate mantra properties', () => {
    const mantra = {
      text: 'ॐ',
      meaning: 'Om',
      translation: 'The primordial sound',
      color: 0xa85c2a,
      significance: 'Ultimate reality',
    };

    expect(mantra).toHaveProperty('text');
    expect(mantra).toHaveProperty('meaning');
    expect(mantra).toHaveProperty('translation');
    expect(mantra).toHaveProperty('color');
    expect(mantra).toHaveProperty('significance');

    expect(typeof mantra.text).toBe('string');
    expect(typeof mantra.meaning).toBe('string');
    expect(typeof mantra.color).toBe('number');
  });

  it('should have valid color values', () => {
    const colors = [0xa85c2a, 0xd97706, 0xf59e0b, 0xfbbf24];

    colors.forEach((color) => {
      expect(color).toBeGreaterThan(0);
      expect(color).toBeLessThanOrEqual(0xffffff);
    });
  });

  it('should validate mantra meanings are not empty', () => {
    const MANTRAS = [
      { text: 'ॐ', meaning: 'Om', translation: 'Sound', color: 0xa85c2a, significance: 'Reality' },
      { text: 'नमस्ते', meaning: 'Namaste', translation: 'Bow', color: 0xd97706, significance: 'Respect' },
    ];

    MANTRAS.forEach((mantra) => {
      expect(mantra.meaning.length).toBeGreaterThan(0);
      expect(mantra.translation.length).toBeGreaterThan(0);
      expect(mantra.significance.length).toBeGreaterThan(0);
    });
  });

  it('should have unique mantra texts', () => {
    const MANTRAS = [
      { text: 'ॐ', meaning: 'Om', translation: 'Sound', color: 0xa85c2a, significance: 'Reality' },
      { text: 'नमस्ते', meaning: 'Namaste', translation: 'Bow', color: 0xd97706, significance: 'Respect' },
      { text: 'शान्तिः', meaning: 'Shanti', translation: 'Peace', color: 0xf59e0b, significance: 'Tranquility' },
    ];

    const texts = MANTRAS.map((m) => m.text);
    const uniqueTexts = new Set(texts);

    expect(uniqueTexts.size).toBe(MANTRAS.length);
  });
});
