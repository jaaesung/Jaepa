import { test, expect } from '@playwright/test';

test.describe('Home Page', () => {
  test('should navigate to the home page', async ({ page }) => {
    await page.goto('/');
    
    // 홈페이지 타이틀 확인
    await expect(page).toHaveTitle(/JaePa/);
  });

  test('should have navigation links', async ({ page }) => {
    await page.goto('/');
    
    // 네비게이션 링크 확인
    const navLinks = page.locator('nav a');
    await expect(navLinks).toHaveCount(3); // 예상되는 링크 수에 맞게 조정
  });

  test('should navigate to different pages', async ({ page }) => {
    await page.goto('/');
    
    // 대시보드 링크 클릭
    await page.getByRole('link', { name: /dashboard/i }).click();
    await expect(page).toHaveURL(/.*dashboard/);
    
    // 뉴스 링크 클릭
    await page.getByRole('link', { name: /news/i }).click();
    await expect(page).toHaveURL(/.*news/);
    
    // 분석 링크 클릭
    await page.getByRole('link', { name: /analysis/i }).click();
    await expect(page).toHaveURL(/.*analysis/);
  });
});
