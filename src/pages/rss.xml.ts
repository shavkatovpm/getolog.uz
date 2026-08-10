import type { APIRoute } from "astro";
import { articles } from "../data/articles";
import { landingPages } from "../data/landing";

const SITE = "https://getolog.uz";

function escapeXml(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}

type FeedItem = {
  title: string;
  description: string;
  url: string;
  date: string;
  category: string;
};

export const GET: APIRoute = () => {
  const items: FeedItem[] = [
    ...landingPages.map((p) => ({
      title: p.h1.uz,
      description: p.answer.uz,
      url: `${SITE}/${p.slug}`,
      date: p.updated,
      category: p.category.uz,
    })),
    ...articles.map((a) => ({
      title: a.title.uz,
      description: a.description.uz,
      url: `${SITE}/blog/${a.slug}`,
      date: a.updated || a.date,
      category: a.category.uz,
    })),
  ].sort((a, b) => b.date.localeCompare(a.date));

  const body = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Getolog — Telegram kanal monetizatsiyasi</title>
    <link>${SITE}</link>
    <description>Pullik Telegram kanal va guruhlar uchun obuna avtomatlashtirish: to'lov, bir martalik invite-link, muddat nazorati.</description>
    <language>uz</language>
    <atom:link href="${SITE}/rss.xml" rel="self" type="application/rss+xml" />
${items
  .map(
    (item) => `    <item>
      <title>${escapeXml(item.title)}</title>
      <link>${item.url}</link>
      <guid isPermaLink="true">${item.url}</guid>
      <description>${escapeXml(item.description)}</description>
      <category>${escapeXml(item.category)}</category>
      <pubDate>${new Date(item.date).toUTCString()}</pubDate>
    </item>`,
  )
  .join("\n")}
  </channel>
</rss>
`;

  return new Response(body, {
    headers: { "Content-Type": "application/xml; charset=utf-8" },
  });
};
