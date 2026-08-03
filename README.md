# RPG — three.js animation

A three.js project scaffolded with [Vite](https://vitejs.dev/).

## Getting started

```bash
npm install
npm run dev
```

Then open the URL Vite prints (default: http://localhost:5173).

## Scripts

- `npm run dev` — start the dev server with hot reload
- `npm run build` — production build to `dist/`
- `npm run preview` — serve the production build locally

## Project structure

```
index.html      # Entry page, full-screen canvas container
src/main.js     # Scene, camera, renderer, lights, and animation loop
public/images/  # Drop images here; reference them as /images/<name>
```

Files in `public/` are served as-is from the site root. For example,
`public/images/hero.png` is available at `/images/hero.png`:

```js
const texture = new THREE.TextureLoader().load('/images/hero.png');
```

The starter scene renders a spinning, bobbing cube over a ground grid, with
orbit controls (drag to rotate, scroll to zoom). Replace the cube in
`src/main.js` with your own animation.
