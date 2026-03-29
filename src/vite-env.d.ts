/// <reference types="vite/client" />

declare module '*.json' {
  const value: any;
  export default value;
}

declare module '../../config/app.config.json' {
  const config: import('./lib/types').AppConfig;
  export default config;
}
