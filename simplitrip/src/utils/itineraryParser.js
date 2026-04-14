/**
 * itineraryParser - Splits a markdown itinerary into structured day cards.
 *
 * Handles two common backend outputs:
 *   1. Heading-based, e.g. "**Day 1**" / "### Day 2 : Title"
 *   2. Table-based, e.g. "| **Day 1** | Morning | Afternoon | ... | Cost |"
 *
 * Costs are detected as explicit price hints like ₹500 / $200 / £30.
 */

const normalizeSpaces = (s = '') => String(s).replace(/[\u202f\u00a0]/g, ' ');

export const hasDayStructure = (markdown = '') =>
  /\bDay\s*(\d+)\b/i.test(normalizeSpaces(markdown));

export const parseItinerary = (markdown = '') => {
  const text = normalizeSpaces(markdown).trim();
  if (!text) return { summary: '', days: [] };

  const lines = text.split('\n');
  const days = [];
  const summaryParts = [];
  let currentDay = null;

  const startDay = (num, title) => {
    currentDay = { dayNumber: num, title: (title || '').trim() || `Day ${num}`, items: [], costs: [] };
    days.push(currentDay);
  };

  const addItem = (day, raw, explicitRemoveDay) => {
    const clean = raw.replace(/[*`]/g, '').replace(/\|/g, '').trim();
    if (!clean) return;
    if (explicitRemoveDay && /\bDay\s*\d+\b/i.test(clean)) return;
    const costMatch = clean.match(/([₹$£€])\s?([\d,]+)\b/i);
    const item = { text: clean, cost: costMatch ? costMatch[2] : null };
    if (costMatch) day.costs.push(parseInt(costMatch[2].replace(/,/g, ''), 10));
    day.items.push(item);
  };

  for (const raw of lines) {
    const line = raw.trim();

    // --- Table row: "| **Day 1** | Morning | Afternoon | ... |" ---
    if (line.startsWith('|')) {
      const cells = line.replace(/^\||\|$/g, '').split('|')
        .map((c) => c.replace(/[*`]/g, '').trim());
      const dayIdx = cells.findIndex((c) => /\bDay\s*(\d+)\b/i.test(c));
      if (dayIdx >= 0) {
        const dayMatch = cells[dayIdx].match(/\bDay\s*(\d+)\b/i);
        startDay(dayMatch[1], cells[dayIdx + 1] || undefined);
        for (let k = dayIdx + 1; k < cells.length; k++) addItem(currentDay, cells[k], true);
      } else if (currentDay) {
        for (let k = 0; k < cells.length; k++) addItem(currentDay, cells[k], false);
      }
      continue;
    }

    // --- Heading / bullet: "**Day 2** : Title" (table-headed or block style) ---
    const heading = line.match(/^#{1,4}\s*Day\s*(\d+)\s*[:\-–—-]?\s*(.*)$/i)
      || line.match(/^-\s*\*{0,2}Day\s*(\d+)\s*[:\-–—-]?\s*\*{0,2}\s*(.*)$/i)
      || line.match(/^\*{0,2}Day\s*(\d+)\s*[:\-–—-]?\s*\*{0,2}\s*(.*)$/i);
    if (heading && heading[1]) {
      startDay(heading[1], heading[2] || undefined);
      continue;
    }

    if (currentDay) {
      addItem(currentDay, line, false);
    } else if (line) {
      summaryParts.push(raw);
    }
  }

  return {
    summary: summaryParts.join('\n').trim(),
    days: days.map((d) => ({ ...d, totalCost: d.costs.reduce((a, b) => a + b, 0) })),
  };
};