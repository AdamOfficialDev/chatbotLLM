'use client';

import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus, oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism';
import remarkGfm from 'remark-gfm';
import { Copy, Check } from 'lucide-react';
import { useState } from 'react';

export default function MarkdownMessage({ content, darkMode = false }) {
  const [copiedCode, setCopiedCode] = useState(null);

  const copyToClipboard = async (code, index) => {
    try {
      await navigator.clipboard.writeText(code);
      setCopiedCode(index);
      setTimeout(() => setCopiedCode(null), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const components = {
'use client';

import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus, oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism';
import remarkGfm from 'remark-gfm';
import { Copy, Check, FileText, Terminal } from 'lucide-react';
import { useState } from 'react';

export default function MarkdownMessage({ content, darkMode = false }) {
  const [copiedCode, setCopiedCode] = useState(null);

  const copyToClipboard = async (code, index) => {
    try {
      await navigator.clipboard.writeText(code);
      setCopiedCode(index);
      setTimeout(() => setCopiedCode(null), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  // Enhanced language detection and icon mapping
  const getLanguageIcon = (language) => {
    const iconMap = {
      'javascript': '🟨',
      'js': '🟨',
      'typescript': '🔷',
      'ts': '🔷',
      'python': '🐍',
      'py': '🐍',
      'java': '☕',
      'cpp': '⚡',
      'c': '⚡',
      'html': '🌐',
      'css': '🎨',
      'sql': '🗄️',
      'bash': '💻',
      'shell': '💻',
      'json': '📦',
      'xml': '📄',
      'yaml': '📝',
      'yml': '📝',
      'markdown': '📝',
      'md': '📝',
      'php': '🐘',
      'go': '🔵',
      'rust': '🦀',
      'ruby': '💎',
      'swift': '🍎',
      'kotlin': '🟣',
      'dart': '🎯'
    };
    return iconMap[language?.toLowerCase()] || <FileText className="h-3 w-3" />;
  };

  const components = {
    code({ node, inline, className, children, ...props }) {
      const match = /language-(\w+)/.exec(className || '');
      const language = match ? match[1] : '';
      const code = String(children).replace(/\n$/, '');
      const codeIndex = `${language}-${code.slice(0, 20)}`;

      if (!inline && match) {
        return (
          <div className="relative group my-4 overflow-hidden rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
            {/* Enhanced header with better styling */}
            <div className="flex items-center justify-between bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-750 px-4 py-3 border-b border-gray-200 dark:border-gray-600">
              <div className="flex items-center gap-2">
                <span className="text-lg">
                  {getLanguageIcon(language)}
                </span>
                <span className="text-sm font-semibold text-gray-700 dark:text-gray-300 capitalize">
                  {language || 'Code'}
                </span>
                <span className="text-xs text-gray-500 dark:text-gray-400 bg-gray-200 dark:bg-gray-700 px-2 py-1 rounded-full">
                  {code.split('\n').length} lines
                </span>
              </div>
              <button
                onClick={() => copyToClipboard(code, codeIndex)}
                className="flex items-center gap-2 px-3 py-1.5 text-xs text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 rounded-lg border border-gray-300 dark:border-gray-600 transition-all duration-200 shadow-sm hover:shadow-md"
                title="Copy code"
              >
                {copiedCode === codeIndex ? (
                  <>
                    <Check className="h-3 w-3 text-green-600" />
                    <span className="font-medium text-green-600">Copied!</span>
                  </>
                ) : (
                  <>
                    <Copy className="h-3 w-3" />
                    <span className="font-medium">Copy</span>
                  </>
                )}
              </button>
            </div>
            
            {/* Enhanced syntax highlighter */}
            <div className="relative">
              <SyntaxHighlighter
                style={darkMode ? vscDarkPlus : oneLight}
                language={language}
                PreTag="div"
                className="!mt-0 !mb-0 !rounded-t-none !rounded-b-xl"
                customStyle={{
                  margin: 0,
                  borderTopLeftRadius: 0,
                  borderTopRightRadius: 0,
                  borderBottomLeftRadius: '0.75rem',
                  borderBottomRightRadius: '0.75rem',
                  fontSize: '14px',
                  lineHeight: '1.5',
                  padding: '1.25rem',
                  background: darkMode ? '#1e1e1e' : '#fafafa',
                }}
                showLineNumbers={code.split('\n').length > 5}
                lineNumberStyle={{
                  minWidth: '2.5em',
                  paddingRight: '1em',
                  color: darkMode ? '#6b7280' : '#9ca3af',
                  fontSize: '12px'
                }}
                wrapLines={true}
                wrapLongLines={true}
                {...props}
              >
                {code}
              </SyntaxHighlighter>
            </div>
          </div>
        );
      }

      return (
        <code
          className={`${className} bg-gray-100 dark:bg-gray-700 text-pink-600 dark:text-pink-400 px-2 py-1 rounded-md text-sm font-mono border border-gray-200 dark:border-gray-600`}
          {...props}
        >
          {children}
        </code>
      );
    },
    // Customize other markdown elements
    h1: ({ children }) => (
      <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4 mt-6 first:mt-0">
        {children}
      </h1>
    ),
    h2: ({ children }) => (
      <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-3 mt-5">
        {children}
      </h2>
    ),
    h3: ({ children }) => (
      <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2 mt-4">
        {children}
      </h3>
    ),
    h4: ({ children }) => (
      <h4 className="text-base font-medium text-gray-900 dark:text-gray-100 mb-2 mt-3">
        {children}
      </h4>
    ),
    p: ({ children }) => (
      <p className="text-gray-800 dark:text-gray-200 mb-3 leading-relaxed">
        {children}
      </p>
    ),
    ul: ({ children }) => (
      <ul className="list-disc list-inside text-gray-800 dark:text-gray-200 mb-3 space-y-1">
        {children}
      </ul>
    ),
    ol: ({ children }) => (
      <ol className="list-decimal list-inside text-gray-800 dark:text-gray-200 mb-3 space-y-1">
        {children}
      </ol>
    ),
    li: ({ children }) => (
      <li className="text-gray-800 dark:text-gray-200">{children}</li>
    ),
    blockquote: ({ children }) => (
      <blockquote className="border-l-4 border-gray-300 dark:border-gray-600 pl-4 py-2 italic text-gray-700 dark:text-gray-300 my-3 bg-gray-50 dark:bg-gray-800/50 rounded-r">
        {children}
      </blockquote>
    ),
    strong: ({ children }) => (
      <strong className="font-semibold text-gray-900 dark:text-gray-100">
        {children}
      </strong>
    ),
    em: ({ children }) => (
      <em className="italic text-gray-800 dark:text-gray-200">{children}</em>
    ),
    table: ({ children }) => (
      <div className="overflow-x-auto my-3">
        <table className="min-w-full border border-gray-200 dark:border-gray-700 rounded-lg">
          {children}
        </table>
      </div>
    ),
    thead: ({ children }) => (
      <thead className="bg-gray-50 dark:bg-gray-800">{children}</thead>
    ),
    tbody: ({ children }) => (
      <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
        {children}
      </tbody>
    ),
    tr: ({ children }) => <tr>{children}</tr>,
    th: ({ children }) => (
      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider border-b border-gray-200 dark:border-gray-700">
        {children}
      </th>
    ),
    td: ({ children }) => (
      <td className="px-4 py-2 text-sm text-gray-800 dark:text-gray-200">
        {children}
      </td>
    ),
    a: ({ children, href }) => (
      <a
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        className="text-blue-600 dark:text-blue-400 hover:underline"
      >
        {children}
      </a>
    ),
    hr: () => (
      <hr className="my-4 border-gray-200 dark:border-gray-700" />
    ),
  };

  return (
    <div className="prose prose-sm max-w-none">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={components}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}