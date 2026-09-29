// Golden-path smoke test (Playwright). Runs in CI against the PUBLIC URL after every deploy.
// Adapt the BEATS array to the demo script. Keep it fast (< 2 min) and focused on the story.
import { test, expect, Page } from '@playwright/test';

const BASE_URL = process.env.PUBLIC_URL; // set by the CI deploy step, never hardcoded
// Which data mode each screen should show once its slice is real: 'live' | 'sample'
// Flip entries to 'live' as slices land, so a silent fallback fails the build.
const BEATS: { name: string; path: string; expectText: RegExp; mode: 'live' | 'sample'; action?: (p: Page) => Promise<void> }[] = [
  { name: 'hello-world', path: '/', expectText: /Dark Factory/i, mode: 'live' },
];

test('golden path works on the public URL', async ({ page }) => {
  expect(BASE_URL, 'PUBLIC_URL must be set').toBeTruthy();
  const consoleErrors: string[] = [];
  const badResponses: string[] = [];
  page.on('console', (m) => { if (m.type() === 'error') consoleErrors.push(m.text()); });
  page.on('response', (r) => { if (r.status() >= 400) badResponses.push(`${r.status()} ${r.url()}`); });

  for (const beat of BEATS) {
    await test.step(beat.name, async () => {
      await page.goto(new URL(beat.path, BASE_URL).toString());
      if (beat.action) await beat.action(page);
      await expect(page.getByText(beat.expectText).first()).toBeVisible({ timeout: 30_000 });
      // Convention: every screen renders data-mode="live|sample|fixture" on its root element.
      await expect(page.locator(`[data-mode="${beat.mode}"]`).first()).toBeVisible();
    });
  }

  expect(consoleErrors, 'console errors').toEqual([]);
  expect(badResponses, 'failed network calls').toEqual([]);
});

test('/health responds ok', async ({ request }) => {
  expect(BASE_URL, 'PUBLIC_URL must be set').toBeTruthy();
  const res = await request.get(new URL('/health', BASE_URL).toString());
  expect(res.status()).toBe(200);
  const body = await res.json();
  expect(body.status).toBe('ok');
});
