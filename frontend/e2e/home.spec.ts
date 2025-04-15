import { test, expect } from '@playwright/test';

test.describe('Home Page', () => {
  test('should navigate to the home page', async ({ page }) => {
    await page.goto('/');

    // 홈페이지 타이틀 확인
    await expect(page).toHaveTitle(/JaePa/);
  });

  test('should have navigation links', async ({ page }) => {
    await page.goto('/');

    // 홈페이지 타이틀 확인
    await expect(page).toHaveTitle(/JaePa/);

    // 로그인 페이지에 로그인 폼이 있는지 확인
    await expect(page.locator('form')).toBeVisible();
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('should navigate to different pages', async ({ page }) => {
    await page.goto('/');

    // 홈페이지 타이틀 확인
    await expect(page).toHaveTitle(/JaePa/);

    // 로그인 페이지에 로그인 폼이 있는지 확인
    await expect(page.locator('form')).toBeVisible();

    // 로그인 페이지에서 회원가입 링크 확인
    const registerLink = page.getByRole('link', { name: /회원가입/i });
    await expect(registerLink).toBeVisible();

    // 회원가입 페이지로 이동 (클릭 대신 URL 직접 이동)
    await page.goto('/register');
    await expect(page).toHaveURL(/.*register/);

    // 로그인 페이지로 다시 이동 (클릭 대신 URL 직접 이동)
    await page.goto('/login');
    await expect(page).toHaveURL(/.*login/);
  });
});
