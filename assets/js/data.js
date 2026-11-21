/* Family Jigsaw Puzzles: puzzle sizes, materials, picture treatments, backdrops, prices and settings.
   src/build.py reads this file (with node), so it is the one source of truth. */
var FJP = window.FJP = window.FJP || {};

FJP.config = {
  // Waitlist sign-ups are emailed to hello@ via FormSubmit (formsubmit.co), the same as the other Our Family Presents sites.
  formEndpoint: "https://formsubmit.co/ajax/hello@familyboardbooks.com",
  email: "hello@familyboardbooks.com",
  foundingDiscount: 15,
  site: "https://www.familyjigsawpuzzles.com",
  storybooks: "https://www.familystorybooks.co.uk",
  boardBooks: "https://www.familyboardbooks.com",
  learnToRead: "https://www.familylearntoread.com",
  umbrella: "https://www.ourfamilypresents.com",
  // Shared photo and cartoon service (the Family Board Books worker). Not used yet: stage 1 is a coming-soon site.
  api: "https://familyboardbooks-api.silent-forest-c98a.workers.dev",
  // Checkout opens later, through the shared Shopify store, with SKUs starting FJP-.
  shopify: { checkoutLive: false, skuPrefix: "FJP-" },
  // Printers chosen by David on 21 Nov 2026: Prodigi (UK) for cardboard, Merchize for wood.
  printers: { card: "Prodigi", wood: "Merchize" }
};

/* Shipping regions, the same as the other sites. Ordering is closed in both until checkout opens. */
FJP.regions = {
  uk: { id: "uk", label: "UK · £", name: "United Kingdom", currency: "£", notice: "" },
  eu: { id: "eu", label: "EU · €", name: "Europe", currency: "€", notice: "" }
};

/* Cardboard puzzles (printed by Prodigi in the UK). w and h are the finished puzzle in millimetres (landscape).
   card is the launch price in euros. PROVISIONAL until Prodigi's trade prices and postage are confirmed.
   UK prices in pounds come from the fixed table FJP.gbp, keyed by the euro price. */
FJP.sizes = [
  { id: "p30",   pieces: 30,   w: 250, h: 200, who: "Ages 3 and up", line: "Big chunky pieces for little hands.", card: 29, color: "#FFC21A", grid: [6, 5] },
  { id: "p110",  pieces: 110,  w: 250, h: 200, who: "Ages 6 and up", line: "A first proper puzzle, done in an afternoon.", card: 32, color: "#1FB45A", grid: [11, 10] },
  { id: "p252",  pieces: 252,  w: 375, h: 285, who: "Ages 9 and up", line: "Our most popular size: a cosy evening's puzzle.", card: 36, color: "#16A6E3", grid: [18, 14] },
  { id: "p500",  pieces: 500,  w: 530, h: 390, who: "Teens and adults", line: "A weekend project for the whole family.", card: 42, color: "#8A3FD9", grid: [25, 20] },
  { id: "p1000", pieces: 1000, w: 765, h: 525, who: "Puzzle lovers", line: "The big one. Clear the dining table.", card: 49, color: "#EE4B2B", grid: [40, 25] }
];

/* Wooden puzzles (printed by Merchize): 3 mm laser-cut wood in a gift box, three sizes.
   Merchize doesn't publish piece counts, so we show the size only until a sample confirms them. Prices PROVISIONAL. */
FJP.woodSizes = [
  { id: "w-s", name: "Small", w: 240, h: 170, price: 39, line: "A cosy keepsake, lovely for younger puzzlers." },
  { id: "w-m", name: "Medium", w: 330, h: 245, price: 45, line: "Our favourite for a family photo." },
  { id: "w-l", name: "Large", w: 410, h: 300, price: 52, line: "The showpiece, for the mantelpiece afterwards." }
];

FJP.materials = [
  { id: "card", name: "Classic cardboard", line: "Thick, glossy board with a snug fit, in a gift tin with your picture on the lid. Made in the UK.",
    points: ["Glossy photo finish", "Pieces that lock together firmly", "Gift tin with your picture on the lid"] },
  { id: "wood", name: "Real wood", line: "Laser-cut wooden pieces with a crisp, bright print. An heirloom to do again and again.",
    points: ["3 mm laser-cut wood, smooth edges", "Three sizes, from 24 to 41 cm wide", "Presented in a keepsake box"] }
];

/* Picture treatments: the same styles as the Family Board Books cartoons, plus the original photo. */
FJP.treatments = [
  { id: "photo", name: "Your photo", line: "Just as you took it, colour-corrected and sharpened for print." },
  { id: "splash", name: "Cartoon Splash", line: "Bold, bright cartoon portraits on paint splats. Our signature look." },
  { id: "painted", name: "Painted Splash", line: "Painterly portraits that stay closest to your photos." },
  { id: "watercolour", name: "Watercolour", line: "Soft, gentle washes of colour." },
  { id: "comic", name: "Comic Pop", line: "Strong outlines, flat colours and halftone dots." },
  { id: "storybook", name: "Storybook", line: "Warm, classic picture-book illustration." }
];

/* Backdrops: put your family somewhere new. Our own drawings, never stock photos of real people. */
FJP.backdrops = [
  { id: "keep", name: "Keep my background" },
  { id: "paris", name: "Paris" },
  { id: "beach", name: "Seaside" },
  { id: "snow", name: "Snowy mountains" },
  { id: "space", name: "Outer space" },
  { id: "jungle", name: "Jungle" }
];

FJP.gbp = { 29: 25, 32: 28, 36: 31, 39: 34, 42: 36, 45: 39, 49: 42, 52: 45 };

FJP.esc = function (s) {
  return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; });
};
