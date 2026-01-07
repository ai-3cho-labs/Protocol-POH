'use client';

import Script from 'next/script';

declare global {
  interface Window {
    UnicornStudio?: { isInitialized: boolean; init: () => void };
  }
}

/**
 * WebGL Background component
 * Full-page animated background using Unicorn.studio
 * - Fixed position behind all content
 * - 25% opacity for subtle effect
 * - Fades out before footer
 * - Mouse-responsive interactivity
 */
export function WebGLBackground() {
  const handleLoad = () => {
    if (window.UnicornStudio && !window.UnicornStudio.isInitialized) {
      window.UnicornStudio.init();
      window.UnicornStudio.isInitialized = true;
    }
  };

  return (
    <>
      {/* WebGL Canvas Container */}
      <div
        data-us-project="JTSmgsU2H8u70gWo7lXy"
        className="fixed inset-0 w-full h-full -z-10 opacity-25 pointer-events-auto"
        aria-hidden="true"
      />

      {/* Footer fade gradient */}
      <div
        className="fixed bottom-0 left-0 right-0 h-48 -z-10 bg-gradient-to-t from-bg-dark to-transparent pointer-events-none"
        aria-hidden="true"
      />

      {/* Unicorn.studio SDK */}
      <Script
        src="https://cdn.jsdelivr.net/gh/hiunicornstudio/unicornstudio.js@v2.0.0/dist/unicornStudio.umd.js"
        onLoad={handleLoad}
        strategy="lazyOnload"
      />
    </>
  );
}
