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
    code({ node, inline, className, children, ...props }) {
      const match = /language-(\w+)/.exec(className || '');
      const language = match ? match[1] : '';
      const code = String(children).replace(/\n$/, '');
      const codeIndex = `${language}-${code.slice(0, 20)}`;

      if (!inline && match) {
        return (
          <div className="relative group my-3">
            <div className="flex items-center justify-between bg-gray-100 dark:bg-gray-800 px-3 py-2 rounded-t-lg border-b border-gray-200 dark:border-gray-600">
              <span className="text-xs font-medium text-gray-600 dark:text-gray-400 uppercase">
                {language}
              </span>
              <button
                onClick={() => copyToClipboard(code, codeIndex)}
                className="flex items-center gap-1 px-2 py-1 text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 rounded transition-colors"
                title="Copy code"
              >
                {copiedCode === codeIndex ? (
                  <>
                    <Check className="h-3 w-3" />
                    Copied
                  </>
                ) : (
                  <>
                    <Copy className="h-3 w-3" />
                    Copy
                  </>
                )}
              </button>
            </div>
            <SyntaxHighlighter
              style={darkMode ? vscDarkPlus : oneLight}
              language={language}
              PreTag="div"
              className="!mt-0 !rounded-t-none"
              customStyle={{
                margin: 0,
                borderTopLeftRadius: 0,
                borderTopRightRadius: 0,
              }}
              {...props}
            >
              {code}
            </SyntaxHighlighter>
          </div>
        );
      }

      return (
        <code
          className={`${className} bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 px-1.5 py-0.5 rounded text-sm font-mono`}
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