import type { AppProps } from "next/app";
import "../styles/globals.css";

// Root app wrapper (keeps logic identical)
export default function App({ Component, pageProps }: AppProps) {
  return <Component {...pageProps} />;
}
