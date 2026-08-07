import { describe, expect, it } from "vitest";

import { tokenStorage } from "@/api/client";

describe("tokenStorage", () => {
  it("stores and clears the access token for the current browser session", () => {
    tokenStorage.clear();
    tokenStorage.set("test-token");

    expect(tokenStorage.get()).toBe("test-token");

    tokenStorage.clear();
    expect(tokenStorage.get()).toBeNull();
  });
});
