"use client"
import { useEffect } from 'react';

export default function ServiceWorkerRegistration() {
  useEffect(() => {
    if ('serviceWorker' in navigator) {
      // Check if the service worker file exists before registering
      fetch('/service-worker.js')
        .then(response => {
          if (response.status === 200) {
            // File exists, register the service worker
            navigator.serviceWorker.register('/service-worker.js')
              .then(registration => {
                console.log('Service Worker registered with scope:', registration.scope);
              })
              .catch(error => {
                console.error('Service Worker registration failed:', error);
              });
          } else {
            console.warn('Service worker file not found, skipping registration');
          }
        })
        .catch(error => {
          console.warn('Could not check for service worker file:', error);
        });
    }
  }, []);

  return null;
}