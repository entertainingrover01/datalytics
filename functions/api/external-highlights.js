// Cloudflare Pages Function: GET /api/external-highlights
// Replaces the Flask endpoint of the same name. Fetches the KDnuggets RSS
// feed server-side and returns up to 6 items as JSON:
//   [{ title, summary, url }]
// Cached at the edge for 1 hour, the same refresh interval the old Flask
// app used for its in-memory cache. Returns [] if the feed cannot be read,
// so the homepage highlights section degrades gracefully.

const RSS_FEED_URL = "https://www.kdnuggets.com/feed";
const MAX_ITEMS = 6;
const SUMMARY_MAX_LENGTH = 150;

function decodeEntities(text) {
  return text
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&#x27;/g, "'")
    .replace(/&apos;/g, "'");
}

function stripCdata(text) {
  return text.replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g, "$1");
}

function stripTags(text) {
  return text.replace(/<[^>]*>/g, "");
}

function extractTag(itemXml, tag) {
  const match = itemXml.match(new RegExp(`<${tag}[^>]*>([\\s\\S]*?)<\\/${tag}>`, "i"));
  if (!match) return "";
  return decodeEntities(stripCdata(match[1]).trim());
}

export async function onRequest() {
  try {
    const response = await fetch(RSS_FEED_URL, {
      headers: { "User-Agent": "Datalytics/1.0 (Cloudflare Pages Function)" },
      cf: { cacheTtl: 3600, cacheEverything: true },
    });
    if (!response.ok) throw new Error(`Feed returned ${response.status}`);
    const xml = await response.text();

    const items = [...xml.matchAll(/<item>([\s\S]*?)<\/item>/gi)]
      .slice(0, MAX_ITEMS)
      .map((m) => {
        const itemXml = m[1];
        const title = extractTag(itemXml, "title") || "No Title";
        let summary = stripTags(extractTag(itemXml, "description") || "");
        if (summary.length > SUMMARY_MAX_LENGTH) {
          summary = summary.slice(0, SUMMARY_MAX_LENGTH) + "...";
        }
        return { title, summary, url: extractTag(itemXml, "link") || "#" };
      });

    return new Response(JSON.stringify(items), {
      headers: {
        "Content-Type": "application/json",
        "Cache-Control": "public, s-maxage=3600, max-age=300",
      },
    });
  } catch (error) {
    console.error("external-highlights failed:", error);
    return new Response(JSON.stringify([]), {
      headers: { "Content-Type": "application/json", "Cache-Control": "no-store" },
    });
  }
}
