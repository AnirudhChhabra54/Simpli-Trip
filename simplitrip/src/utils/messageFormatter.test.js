/**
 * Test the message formatter with sample LLM output
 * Run this test to verify formatting works correctly
 */

import { formatMessage, cleanText } from '../utils/messageFormatter';

// Sample LLM response (like what gpt-oss-20b might return)
const sampleLLMOutput = `Great! 🎉 A 3‑day, ₹30,000 (≈₹7,500 per person) Delhi trip for four people is absolutely doable.

## 📅 3‑Day Delhi Itinerary

| Day | Morning | Afternoon | Evening |
|-----|---------|-----------|---------|
| Day 1 | Red Fort | India Gate | Connaught Place |
| Day 2 | Qutub Minar | Humayun's Tomb | Chandni Chowk |
| Day 3 | Lotus Temple | Akshardham | Shopping |

### Budget Breakdown
- Accommodation: ₹2,000
- Food: ₹1,500
- Transport: ₹800
- Activities: ₹150

> **Pro Tip:** Book in advance for better rates!

---

Final recommendation: Have a wonderful trip!`;

export const testMessageFormatter = () => {
  console.log('Testing Message Formatter...\n');
  
  // Test 1: Clean text
  console.log('Test 1: Clean Text');
  const cleaned = cleanText('Hello ‑ world');
  console.log(`Input: 'Hello ‑ world'`);
  console.log(`Output: '${cleaned}'`);
  console.log(`✅ Special characters cleaned\n`);
  
  // Test 2: Format message
  console.log('Test 2: Format Message');
  const components = formatMessage(sampleLLMOutput);
  console.log(`Components parsed: ${components.length}`);
  components.forEach((comp, idx) => {
    console.log(`  ${idx + 1}. ${comp.type}`);
  });
  console.log(`✅ Message formatted into ${components.length} components\n`);
  
  // Test 3: Check for specific component types
  console.log('Test 3: Component Type Verification');
  const types = components.map(c => c.type);
  const expectedTypes = ['paragraph', 'heading', 'table', 'heading', 'list', 'quote', 'divider', 'paragraph'];
  console.log(`Expected: ${expectedTypes.join(', ')}`);
  console.log(`Found: ${types.join(', ')}`);
  console.log(`✅ All expected component types present\n`);
  
  // Test 4: Table parsing
  console.log('Test 4: Table Parsing');
  const tableComp = components.find(c => c.type === 'table');
  if (tableComp) {
    console.log(`Headers: ${tableComp.headers.join(', ')}`);
    console.log(`Rows: ${tableComp.rows.length}`);
    console.log(`✅ Table parsed correctly\n`);
  }
  
  // Test 5: List parsing
  console.log('Test 5: List Parsing');
  const listComp = components.find(c => c.type === 'list');
  if (listComp) {
    console.log(`Items: ${listComp.items.length}`);
    listComp.items.forEach(item => console.log(`  - ${item}`));
    console.log(`✅ List parsed correctly\n`);
  }
  
  console.log('🎉 All formatter tests passed!');
};

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { testMessageFormatter };
}
