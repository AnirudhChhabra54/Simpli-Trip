// /**
//  * Message Formatter - Converts raw LLM output into refined, visually appealing chat messages
//  * Handles markdown formatting, code blocks, tables, and special content types
//  */

// /**
//  * Parse and format LLM response into structured message components
//  * @param {string} text - Raw LLM response text
//  * @returns {Array} Array of formatted message components
//  */
// export const formatMessage = (text) => {
//   if (!text || typeof text !== 'string') {
//     return [{ type: 'text', content: '' }];
//   }

//   const components = [];
//   let remaining = text.trim();

//   // Split by major sections (headings, tables, lists)
//   const lines = remaining.split('\n');
//   let i = 0;

//   while (i < lines.length) {
//     const line = lines[i];

//     // Skip empty lines
//     if (line.trim() === '') {
//       i++;
//       continue;
//     }

//     // Handle markdown headings (### Day 1, ## 💰 Budget Breakdown)
//     if (line.match(/^#+\s/)) {
//       const level = line.match(/^#+/)[0].length;
//       const title = line.replace(/^#+\s*/, '').trim();
//       components.push({
//         type: 'heading',
//         level,
//         content: title
//       });
//       i++;
//       continue;
//     }

//     // Handle tables (look for | character)
//     if (line.includes('|')) {
//       const tableLines = [line];
//       i++;

//       // Collect all consecutive table lines
//       while (i < lines.length && lines[i].includes('|')) {
//         tableLines.push(lines[i]);
//         i++;
//       }

//       const table = parseTable(tableLines);
//       if (table) {
//         components.push(table);
//       }
//       continue;
//     }

//     // Handle bullet lists
//     if (line.match(/^\s*[-•*]\s/)) {
//       const listItems = [];
//       while (i < lines.length && lines[i].match(/^\s*[-•*]\s/)) {
//         const item = lines[i].replace(/^\s*[-•*]\s*/, '').trim();
//         listItems.push(item);
//         i++;
//       }
//       components.push({
//         type: 'list',
//         items: listItems
//       });
//       continue;
//     }

//     // Handle quotes (>) and tips
//     if (line.startsWith('>')) {
//       const quoteLines = [line.replace(/^\s*>\s*/, '').trim()];
//       i++;
//       while (i < lines.length && lines[i].startsWith('>')) {
//         quoteLines.push(lines[i].replace(/^\s*>\s*/, '').trim());
//         i++;
//       }
//       components.push({
//         type: 'quote',
//         content: quoteLines.join(' ')
//       });
//       continue;
//     }

//     // Handle code blocks (```)
//     if (line.includes('```')) {
//       const codeLines = [];
//       i++; // Skip opening ```
//       while (i < lines.length && !lines[i].includes('```')) {
//         codeLines.push(lines[i]);
//         i++;
//       }
//       i++; // Skip closing ```
//       components.push({
//         type: 'code',
//         content: codeLines.join('\n')
//       });
//       continue;
//     }

//     // Handle horizontal rules
//     if (line.match(/^[-*_]{3,}$/)) {
//       components.push({ type: 'divider' });
//       i++;
//       continue;
//     }

//     // Regular paragraph text
//     const paraLines = [line];
//     i++;
//     while (
//       i < lines.length &&
//       lines[i].trim() !== '' &&
//       !lines[i].match(/^#+\s/) &&
//       !lines[i].includes('|') &&
//       !lines[i].match(/^\s*[-•*]\s/) &&
//       !lines[i].startsWith('>') &&
//       !lines[i].includes('```') &&
//       !lines[i].match(/^[-*_]{3,}$/)
//     ) {
//       paraLines.push(lines[i]);
//       i++;
//     }

//     const paraText = paraLines.join(' ').trim();
//     if (paraText) {
//       components.push({
//         type: 'paragraph',
//         content: formatInlineMarkdown(paraText)
//       });
//     }
//   }

//   return components;
// };

// /**
//  * Parse markdown table into structured format
//  */
// const parseTable = (tableLines) => {
//   if (tableLines.length < 2) return null;

//   const rows = tableLines
//     .map(line =>
//       line
//         .split('|')
//         .map(cell => cell.trim())
//         .filter(cell => cell !== '')
//     )
//     .filter(row => row.length > 0);

//   if (rows.length < 2) return null;

//   // First row is header, second row (if separator) is skipped
//   const headers = rows[0];
//   let dataRows = rows.slice(1);

//   // Skip separator row if it exists (row with dashes)
//   if (dataRows[0] && dataRows[0].every(cell => cell.match(/^-+$/))) {
//     dataRows = dataRows.slice(1);
//   }

//   return {
//     type: 'table',
//     headers,
//     rows: dataRows
//   };
// };

// /**
//  * Format inline markdown (bold, italic, links)
//  */
// const formatInlineMarkdown = (text) => {
//   // This returns text; actual rendering will handle markdown
//   return text;
// };

// /**
//  * Clean up special unicode characters that LLM sometimes uses
//  */
// export const cleanText = (text) => {
//   if (!text) return '';
//   return text
//     .replace(/(\u2011|\u2010)/g, '-') // Replace hyphens
//     .replace(/\u00A0/g, ' ') // Replace non-breaking spaces
//     .replace(/[\u201C\u201D]/g, '"') // Replace smart quotes
//     .trim();
// };

// /**
//  * Render formatted message components to React elements
//  */
// export const renderFormattedMessage = (components) => {
//   return components.map((component, idx) => {
//     switch (component.type) {
//       case 'heading':
//         const headingClass = {
//           1: 'text-2xl font-bold',
//           2: 'text-xl font-bold',
//           3: 'text-lg font-bold',
//           4: 'text-base font-bold'
//         }[component.level] || 'text-lg font-bold';
//         return (
//           <div key={idx} className={`${headingClass} mt-4 mb-2`}>
//             {component.content}
//           </div>
//         );

//       case 'paragraph':
//         return (
//           <p key={idx} className="mb-3 text-gray-700 leading-relaxed">
//             {cleanText(component.content)}
//           </p>
//         );

//       case 'list':
//         return (
//           <ul key={idx} className="mb-3 ml-6 space-y-1">
//             {component.items.map((item, i) => (
//               <li key={i} className="text-gray-700 list-disc">
//                 {cleanText(item)}
//               </li>
//             ))}
//           </ul>
//         );

//       case 'quote':
//         return (
//           <blockquote
//             key={idx}
//             className="mb-3 pl-4 border-l-4 border-blue-400 bg-blue-50 py-2 text-gray-700 italic"
//           >
//             {cleanText(component.content)}
//           </blockquote>
//         );

//       case 'table':
//         return (
//           <div key={idx} className="mb-4 overflow-x-auto">
//             <table className="w-full border-collapse border border-gray-300">
//               <thead className="bg-gray-100">
//                 <tr>
//                   {component.headers.map((header, i) => (
//                     <th
//                       key={i}
//                       className="border border-gray-300 px-3 py-2 text-left font-semibold"
//                     >
//                       {cleanText(header)}
//                     </th>
//                   ))}
//                 </tr>
//               </thead>
//               <tbody>
//                 {component.rows.map((row, i) => (
//                   <tr key={i} className={i % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
//                     {row.map((cell, j) => (
//                       <td
//                         key={j}
//                         className="border border-gray-300 px-3 py-2 text-gray-700"
//                       >
//                         {cleanText(cell)}
//                       </td>
//                     ))}
//                   </tr>
//                 ))}
//               </tbody>
//             </table>
//           </div>
//         );

//       case 'code':
//         return (
//           <pre key={idx} className="mb-3 bg-gray-900 text-gray-100 p-3 rounded overflow-x-auto">
//             <code className="text-sm">{component.content}</code>
//           </pre>
//         );

//       case 'divider':
//         return <hr key={idx} className="my-4 border-gray-300" />;

//       default:
//         return null;
//     }
//   });
// };
import React from 'react';

/**
 * Message Formatter - Enhanced for SimpliTrip
 * Converts raw LLM output into refined, visually appealing chat messages
 * Supports: Headings, Tables, Lists (Ordered/Unordered), Code Blocks, Quotes, and Inline Styles.
 */

/**
 * Parse and format LLM response into structured message components
 * @param {string} text - Raw LLM response text
 * @returns {Array} Array of formatted message components
 */
export const formatMessage = (text) => {
  if (!text || typeof text !== 'string') {
    return [{ type: 'text', content: '' }];
  }

  const components = [];
  const lines = text.trim().split('\n');
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];
    const trimmedLine = line.trim();

    // Skip empty lines
    if (trimmedLine === '') {
      i++;
      continue;
    }

    // 1. Headings (### Title)
    if (line.match(/^#+\s/)) {
      const level = line.match(/^#+/)[0].length;
      const title = line.replace(/^#+\s*/, '').trim();
      components.push({
        type: 'heading',
        level,
        content: title
      });
      i++;
      continue;
    }

    // 2. Horizontal Rules (---)
    if (line.match(/^[-*_]{3,}$/)) {
      components.push({ type: 'divider' });
      i++;
      continue;
    }

    // 3. Code Blocks (```)
    if (line.trim().startsWith('```')) {
      const language = line.trim().replace('```', '');
      const codeLines = [];
      i++; // Skip opening fence
      while (i < lines.length && !lines[i].trim().startsWith('```')) {
        codeLines.push(lines[i]);
        i++;
      }
      i++; // Skip closing fence
      components.push({
        type: 'code',
        language,
        content: codeLines.join('\n')
      });
      continue;
    }

    // 4. Tables (| Col | Col |)
    if (line.trim().startsWith('|')) {
      const tableLines = [line];
      i++;
      while (i < lines.length && lines[i].trim().startsWith('|')) {
        tableLines.push(lines[i]);
        i++;
      }
      const table = parseTable(tableLines);
      if (table) components.push(table);
      continue;
    }

    // 5. Blockquotes (> Text)
    if (line.trim().startsWith('>')) {
      const quoteLines = [line.replace(/^>\s*/, '')];
      i++;
      while (i < lines.length && lines[i].trim().startsWith('>')) {
        quoteLines.push(lines[i].replace(/^>\s*/, ''));
        i++;
      }
      components.push({
        type: 'quote',
        content: quoteLines.join(' ')
      });
      continue;
    }

    // 6. Lists (Unordered and Ordered)
    const isUnordered = /^\s*[-*•]\s/.test(line);
    const isOrdered = /^\s*\d+\.\s/.test(line);

    if (isUnordered || isOrdered) {
      const items = [];
      const listType = isOrdered ? 'ordered' : 'unordered';
      
      // Regex to match the start of a list item
      const itemRegex = isOrdered ? /^\s*\d+\.\s*/ : /^\s*[-*•]\s*/;

      while (i < lines.length) {
        const currentLine = lines[i];
        const isCurrentUnordered = /^\s*[-*•]\s/.test(currentLine);
        const isCurrentOrdered = /^\s*\d+\.\s/.test(currentLine);
        
        // Break if we hit a non-list line or a different type of list
        if ((isOrdered && !isCurrentOrdered) || (!isOrdered && !isCurrentUnordered)) {
          // Allow multi-line list items (indented lines)
          if (currentLine.match(/^\s{2,}/) && items.length > 0) {
            items[items.length - 1] += ' ' + currentLine.trim();
            i++;
            continue;
          }
          break;
        }

        items.push(currentLine.replace(itemRegex, '').trim());
        i++;
      }
      
      components.push({
        type: 'list',
        listType,
        items
      });
      continue;
    }

    // 7. Paragraphs
    const paraLines = [line];
    i++;
    while (
      i < lines.length &&
      lines[i].trim() !== '' &&
      !lines[i].match(/^#+\s/) &&
      !lines[i].trim().startsWith('|') &&
      !lines[i].match(/^\s*[-*•]\s/) &&
      !lines[i].match(/^\s*\d+\.\s/) &&
      !lines[i].trim().startsWith('>') &&
      !lines[i].trim().startsWith('```') &&
      !lines[i].match(/^[-*_]{3,}$/)
    ) {
      paraLines.push(lines[i]);
      i++;
    }
    
    components.push({
      type: 'paragraph',
      content: paraLines.join(' ')
    });
  }

  return components;
};

/**
 * Parse markdown table lines into header and body
 */
const parseTable = (lines) => {
  const cleanRow = (line) => 
    line.split('|')
      .map(c => c.trim())
      .filter((c, idx, arr) => idx > 0 && idx < arr.length - 1); // Remove empty first/last from split

  if (lines.length < 2) return null;

  const headers = cleanRow(lines[0]);
  let rows = lines.slice(1);

  // Remove separator line (e.g. |---|---|)
  if (rows.length > 0 && rows[0].includes('---')) {
    rows = rows.slice(1);
  }

  return {
    type: 'table',
    headers,
    rows: rows.map(cleanRow)
  };
};

/**
 * Clean text for safe rendering
 */
export const cleanText = (text) => {
  if (!text) return '';
  return text
    .replace(/(\u2011|\u2010)/g, '-')
    .replace(/\u00A0/g, ' ')
    .replace(/[\u201C\u201D]/g, '"')
    .trim();
};

/**
 * Parse inline markdown styles (bold, italic, code, link)
 * Returns an array of React Nodes (strings and elements)
 */
const parseInlineStyles = (text) => {
  if (!text) return null;

  // Split by syntax patterns
  // 1. Code: `text`
  // 2. Bold: **text**
  // 3. Italic: *text* or _text_
  // 4. Link: [text](url)
  const regex = /(`[^`]+`|\*\*[^*]+\*\*|\*[^*]+\*|\[[^\]]+\]\([^)]+\))/g;
  
  const parts = text.split(regex);

  return parts.map((part, index) => {
    // Code
    if (part.startsWith('`') && part.endsWith('`')) {
      return (
        <code key={index} className="bg-gray-700 text-cyan-400 px-1.5 py-0.5 rounded text-sm font-mono mx-1">
          {part.slice(1, -1)}
        </code>
      );
    }
    // Bold
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={index} className="text-white font-bold">{part.slice(2, -2)}</strong>;
    }
    // Italic
    if (part.startsWith('*') && part.endsWith('*')) {
      return <em key={index} className="text-gray-300 italic">{part.slice(1, -1)}</em>;
    }
    // Link
    if (part.match(/^\[.*\]\(.*\)$/)) {
      const match = part.match(/^\[(.*)\]\((.*)\)$/);
      if (match) {
        return (
          <a 
            key={index} 
            href={match[2]} 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-cyan-400 hover:text-cyan-300 underline decoration-cyan-500/30 hover:decoration-cyan-300 transition-all"
          >
            {match[1]}
          </a>
        );
      }
    }
    // Plain text
    return part;
  });
};

/**
 * Render Formatted Message Components
 * Using Tailwind CSS classes matching SimpliTrip's Dark/Neon Theme
 */
export const renderFormattedMessage = (components) => {
  return components.map((component, idx) => {
    switch (component.type) {
      case 'heading':
        const HeadingTag = `h${Math.min(component.level, 4)}`;
        const sizeClasses = {
          1: 'text-2xl text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-500',
          2: 'text-xl text-white',
          3: 'text-lg text-cyan-100',
          4: 'text-base text-gray-200'
        }[component.level] || 'text-lg';
        
        return (
          <HeadingTag key={idx} className={`${sizeClasses} font-bold mt-6 mb-3 first:mt-0`}>
            {component.content}
          </HeadingTag>
        );

      case 'paragraph':
        return (
          <p key={idx} className="mb-4 text-gray-300 leading-relaxed text-[15px]">
            {parseInlineStyles(cleanText(component.content))}
          </p>
        );

      case 'list':
        const ListTag = component.listType === 'ordered' ? 'ol' : 'ul';
        const listStyle = component.listType === 'ordered' ? 'list-decimal' : 'list-disc';
        
        return (
          <ListTag key={idx} className={`mb-4 ml-5 space-y-2 ${listStyle} marker:text-cyan-500`}>
            {component.items.map((item, i) => (
              <li key={i} className="text-gray-300 pl-1">
                {parseInlineStyles(cleanText(item))}
              </li>
            ))}
          </ListTag>
        );

      case 'quote':
        return (
          <div key={idx} className="mb-4 relative pl-4 pr-2 py-2 border-l-4 border-cyan-500 bg-gray-800/50 rounded-r-lg">
            <p className="text-gray-400 italic">
              {parseInlineStyles(cleanText(component.content))}
            </p>
          </div>
        );

      case 'table':
        return (
          <div key={idx} className="mb-6 overflow-hidden rounded-xl border border-gray-700 shadow-lg bg-gray-800/40 backdrop-blur-sm">
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="text-xs uppercase bg-gray-900/80 text-cyan-400">
                  <tr>
                    {component.headers.map((header, i) => (
                      <th key={i} className="px-6 py-4 font-bold tracking-wider">
                        {header}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-700">
                  {component.rows.map((row, i) => (
                    <tr key={i} className="hover:bg-gray-700/30 transition-colors">
                      {row.map((cell, j) => (
                        <td key={j} className="px-6 py-4 text-gray-300 whitespace-nowrap">
                          {parseInlineStyles(cleanText(cell))}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        );

      case 'code':
        return (
          <div key={idx} className="mb-4 relative group rounded-xl overflow-hidden border border-gray-700">
            <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
              <span className="text-xs text-gray-500 font-mono px-2 py-1 bg-gray-800 rounded">
                {component.language || 'text'}
              </span>
            </div>
            <pre className="bg-[#0d1117] p-4 overflow-x-auto">
              <code className="text-sm font-mono text-gray-300 leading-relaxed">
                {component.content}
              </code>
            </pre>
          </div>
        );

      case 'divider':
        return <div key={idx} className="my-6 border-t border-gray-700" />;

      default:
        return null;
    }
  });
};