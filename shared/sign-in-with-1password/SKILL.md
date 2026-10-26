---
name: sign-in-with-1password
description: Sign into an existing web account with 1Password autofill through computer use. Use when browser sign-in needs a saved login, including Microsoft work accounts. Not for vault administration, account recovery, or provisioning API secrets.
---

# Sign in with 1Password

Complete the sign-in requested by the user while keeping credentials inside 1Password. Reuse an authenticated session unless the user asks to exercise sign-in separately.

## Select the browser and account

- Use the requested browser, or the existing profile with the installed 1Password extension. Chrome was used for the observed workflow. An isolated agent browser may lack the extension and saved sessions.
- Use native computer-use controls for the browser toolbar and extension popup. If these controls or the extension are unavailable, report that prerequisite instead of retrieving passwords through a different channel.
- Bind page interactions to the exact tab ID or URL. For native input, confirm the active app and tab, especially after closing another tab. Refresh accessibility state after actions because popup windows and element indices change.
- Check the destination host before filling. Match the requested username and saved website. Item titles alone are insufficient when several accounts use the same Microsoft sign-in host. Ask which account to use if the intended identity is ambiguous.

## Fill the sign-in form

Open the 1Password toolbar button, select the matching login, and choose **Autofill** on the site's sign-in form. Continue through the site's normal **Next** or **Sign in** steps when needed. Prefer the app's existing authentication flow so its return destination remains intact.

For a user-requested standalone sign-in check, **Open & Fill** opens the item's saved website. That can lead to the provider's general portal instead of the original app. At a Microsoft account chooser, **Use another account** opens an email form where the correct item can be autofilled. Do not sign the user out to force a challenge.

Keep passwords masked. Do not reveal or copy them, read them into tool output, or export them into commands, configuration, or evidence. Do not transfer browser cookies or session files between profiles. Dismiss incidental **Save item** prompts rather than creating new credential records.

## Handle user checkpoints

- If 1Password is locked or requires Touch ID, have the user unlock it locally. Never request the vault password in chat.
- If the provider requires phone approval, tell the user the account and current matching number when shown. Wait for their approval. Do not repeatedly resend challenges. If it expires, report the expired challenge before starting another attempt.
- Keep remember-device options unchecked. At Microsoft's **Stay signed in?** prompt, choose **No** and leave **Don't show this again** unchecked unless the user explicitly requests persistent sign-in.
- If credentials are rejected, no matching login exists, or the flow requires recovery, credential changes, or new access consent, stop and report that specific checkpoint. Do not try other saved identities as guesses.

## Confirm completion

Observe the signed-in destination and expected account before reporting success. Distinguish reused sessions, completed sign-in, and pending approval. After a separate provider sign-in, return to the exact original app tab and check its state. A completed provider login alone does not prove access to that app.
