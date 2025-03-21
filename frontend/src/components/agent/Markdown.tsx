import Link from "next/link";
import React, { memo } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const NonMemoizedMarkdown = ({ children }: { children: string }) => {
  const components = {
    code: ({ inline, className, children, ...props }: any) => {
      const match = /language-(\w+)/.exec(className || "");
      return !inline && match ? (
        <pre
          {...props}
          className={`${className} text-sm w-[80dvw] md:max-w-[500px] overflow-x-scroll bg-zinc-900 p-3 rounded-lg mt-2 mb-2 font-mono text-gray-200`}
        >
          <code className={match[1]}>{children}</code>
        </pre>
      ) : (
        <code
          className={`${className} text-sm bg-zinc-800 text-gray-200 py-0.5 px-1 rounded-md font-mono`}
          {...props}
        >
          {children}
        </code>
      );
    },
    pre: ({ children, ...props }: any) => {
      return (
        <pre
          className="bg-zinc-900 p-3 rounded-lg mt-2 mb-2 overflow-x-auto w-full font-mono text-sm text-gray-200"
          {...props}
        >
          {children}
        </pre>
      );
    },
    ol: ({ children, ...props }: any) => {
      return (
        <ol className="list-decimal list-outside ml-4 my-2" {...props}>
          {children}
        </ol>
      );
    },
    li: ({ children, ...props }: any) => {
      return (
        <li className="py-1" {...props}>
          {children}
        </li>
      );
    },
    ul: ({ children, ...props }: any) => {
      return (
        <ul className="list-disc list-outside ml-4 my-2" {...props}>
          {children}
        </ul>
      );
    },
    strong: ({ children, ...props }: any) => {
      return (
        <span className="font-semibold" {...props}>
          {children}
        </span>
      );
    },
    a: ({ children, ...props }: any) => {
      return (
        <Link
          className="text-blue-400 hover:underline"
          target="_blank"
          rel="noreferrer"
          {...props}
        >
          {children}
        </Link>
      );
    },
    table: ({ children, ...props }: any) => {
      return (
        <div className="overflow-x-auto my-2">
          <table
            className="border-collapse w-full border border-gray-700"
            {...props}
          >
            {children}
          </table>
        </div>
      );
    },
    th: ({ children, ...props }: any) => {
      return (
        <th
          className="border border-gray-700 bg-gray-800 px-3 py-2 text-left text-sm"
          {...props}
        >
          {children}
        </th>
      );
    },
    td: ({ children, ...props }: any) => {
      return (
        <td className="border border-gray-700 px-3 py-2 text-sm" {...props}>
          {children}
        </td>
      );
    },
    blockquote: ({ children, ...props }: any) => {
      return (
        <blockquote
          className="border-l-4 border-gray-600 pl-4 my-2 italic text-gray-300"
          {...props}
        >
          {children}
        </blockquote>
      );
    },
    h1: ({ children, ...props }: any) => {
      return (
        <h1 className="text-xl font-bold mt-4 mb-2" {...props}>
          {children}
        </h1>
      );
    },
    h2: ({ children, ...props }: any) => {
      return (
        <h2 className="text-lg font-bold mt-3 mb-2" {...props}>
          {children}
        </h2>
      );
    },
    h3: ({ children, ...props }: any) => {
      return (
        <h3 className="text-md font-bold mt-3 mb-1" {...props}>
          {children}
        </h3>
      );
    },
  };

  // Process cybersecurity terminal outputs with special formatting
  const processedContent = children
    .replace(/\$\s(sudo\s.+)/g, "```bash\n$ $1\n```") // Format sudo commands
    .replace(/(\[+)(WARNING|ERROR|INFO|SUCCESS)(\]+)/g, "**[$2]**"); // Highlight log levels

  return (
    <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
      {processedContent}
    </ReactMarkdown>
  );
};

export const Markdown = memo(
  NonMemoizedMarkdown,
  (prevProps, nextProps) => prevProps.children === nextProps.children
);
