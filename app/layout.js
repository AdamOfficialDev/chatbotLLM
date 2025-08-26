import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata = {
  title: 'AI Chatbot - Multi-Provider Chat Interface',
  description: 'Chat with OpenAI, Anthropic, and Google Gemini models using your universal API key',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={inter.className}>
        {children}
      </body>
    </html>
  );
}