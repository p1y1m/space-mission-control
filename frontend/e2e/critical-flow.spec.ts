import { expect, test } from '@playwright/test'
test('operator can authenticate and navigate core workflows', async ({ page }) => {
  const stamp = Date.now(); await page.goto('/login'); await page.getByRole('button',{name:'Create account'}).click()
  await page.getByLabel(/Call sign/).fill('E2E Operator'); await page.getByLabel('Email address').fill(`e2e-${stamp}@example.com`); await page.getByLabel('Passphrase').fill('strong-e2e-password')
  await page.getByRole('button',{name:'Create station'}).click(); await expect(page.getByText('Orbital operations')).toBeVisible()
  await page.getByText('Satellite Explorer').click(); await expect(page.getByText('Satellite explorer')).toBeVisible()
  await page.getByText('Watchlist').click(); await page.getByRole('button',{name:/Add asset/}).click(); await page.locator('.picker button').first().click(); await expect(page.locator('.watch-card')).toBeVisible()
  await page.getByText('Missions').click(); await page.getByRole('button',{name:/New mission/}).click(); await page.getByLabel('Mission name').fill('E2E Survey'); await page.getByRole('button',{name:'Save mission'}).click(); await expect(page.getByText('E2E Survey')).toBeVisible()
  await page.getByRole('button',{name:'Log out'}).click(); await expect(page.getByText('Welcome back, operator')).toBeVisible()
})
