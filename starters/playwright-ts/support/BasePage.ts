import { Page } from '@playwright/test';

/**
 * Base for all page objects. Provides the shared navigation entry point and a hook for
 * app-specific overlays (cookie banners, welcome modals). Subclasses override
 * dismissOverlays() with the SUT's real selectors — see an instance repo for an example.
 */
export class BasePage {
  constructor(protected readonly page: Page) {}

  async goto(path = '/'): Promise<void> {
    await this.page.goto(path);
    await this.dismissOverlays();
  }

  /** Override per SUT. Default is a no-op so it's always safe to call. */
  async dismissOverlays(): Promise<void> {}
}
