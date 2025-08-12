import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeSanitize from 'rehype-sanitize';
import rehypeExternalLinks from 'rehype-external-links';

export default function Markdown({ children }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      rehypePlugins={[[rehypeExternalLinks, { target: '_blank', rel: ['nofollow', 'noopener', 'noreferrer'] }], rehypeSanitize]}
      components={
        {
          code({ inline, className, children, ...props }) {
            if (inline) {
              return <code className="bg-blue-100 text-blue-800 px-2 py-1 rounded-md text-sm font-mono" {...props}>{children}</code>;
            }
            return (
              <pre className="bg-gray-900 text-gray-100 p-4 rounded-xl overflow-auto my-4 shadow-inner">
                <code className={className} {...props}>{children}</code>
              </pre>
            );
          },
          a({ node, ...props }) {
            return <a className="text-blue-600 hover:text-blue-800 underline font-medium transition-colors" {...props} />;
          },
          ul({ node, ...props }) {
            return <ul className="list-disc pl-6 space-y-2 my-4" {...props} />;
          },
          ol({ node, ...props }) {
            return <ol className="list-decimal pl-6 space-y-2 my-4" {...props} />;
          },
          h1({ node, ...props }) {
            return <h1 className="text-2xl font-bold text-gray-900 mb-4 mt-6" {...props} />;
          },
          h2({ node, ...props }) {
            return <h2 className="text-xl font-semibold text-gray-900 mb-3 mt-5" {...props} />;
          },
          h3({ node, ...props }) {
            return <h3 className="text-lg font-semibold text-gray-900 mb-3 mt-4" {...props} />;
          },
          p({ node, ...props }) {
            return <p className="text-gray-700 leading-relaxed mb-4" {...props} />;
          },
          blockquote({ node, ...props }) {
            return <blockquote className="border-l-4 border-blue-500 pl-4 italic text-gray-600 my-4 bg-blue-50 py-2 rounded-r-lg" {...props} />;
          }
        }
      }
    >
      {typeof children === 'string' ? children : String(children ?? '')}
    </ReactMarkdown>
  );
}
