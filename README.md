# Family Jigsaw Puzzles

Website for www.familyjigsawpuzzles.com: jigsaw puzzles made from your family photos, as they are or drawn in our cartoon styles with a backdrop such as Paris, in cardboard or wood. Part of the Our Family Presents group, built on the same design system as Family Board Books, Family Storybooks and Family Learn to Read.

- `assets/js/data.js`  sizes, materials, looks, backdrops, prices and settings (the one source of truth)
- `assets/js/site.js`  wordmark, the looks and backdrops preview, waitlist form
- `assets/css/site.css`  styles, shared with the sister sites plus jigsaw additions
- `src/build.py`  builds the site into `dist/` (`python3 src/build.py`, needs node and Python 3.12+); draws the example puzzle and its cut lines
- `.github/workflows/pages.yml`  publishes `dist/` to GitHub Pages on every push to main

Stage 1 is a coming-soon site with a waitlist (FormSubmit, emails hello@familyboardbooks.com). Printers (chosen 21 Nov 2026): Prodigi (UK) for cardboard, Merchize for wood. Prices are provisional until their trade prices and postage are confirmed.
Nothing uses the shared photo and cartoon service yet. Backdrops (Paris and so on) will need a new drawing mode in that service, agreed in one chat at a time.
Pictures on the site are our own drawings. Customer photos are never published here.
