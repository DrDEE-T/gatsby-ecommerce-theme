# LinkedIn Posting Automation Setup

## Step 1: Create a LinkedIn App

1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/apps)
2. Click "Create app"
3. Fill in:
   - **App name**: `Claude LinkedIn Automation` (or your choice)
   - **LinkedIn Page** (if posting to a company page): Select your page
   - **App logo**: Upload a logo
   - **Legal agreement**: Accept

4. Copy your credentials from the "Auth" tab:
   - **Client ID**
   - **Client Secret**

## Step 2: Set Up Authorized Redirect URI

1. In your app settings, go to "Auth" tab
2. Add **Authorized redirect URI**:
   ```
   http://localhost:3000/api/linkedin/callback
   ```
   (For production, change `localhost:3000` to your actual domain)

## Step 3: Request Access to Sign In With LinkedIn

1. Still in "Auth" tab, look for "Request access"
2. Request these permissions:
   - `w_member_social` - Post, comment, and like on behalf of authenticated member
   - `r_liteprofile_member` - Access member profile information

## Step 4: Get Access Token

Run the OAuth flow:
```bash
node scripts/linkedin-oauth.js
```

This will:
1. Open a browser to LinkedIn login
2. Redirect you back with an auth code
3. Exchange it for an access token
4. Save it to `.env.local`

## Step 5: Add to Environment Variables

Create `.env.local` in project root:
```
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret
LINKEDIN_ACCESS_TOKEN=your_access_token
LINKEDIN_USER_ID=your_linkedin_urn
```

**To get your LinkedIn User ID:**
1. Visit your LinkedIn profile
2. Go to Network tab in Inspect Element
3. Look for requests with your profile ID in the response

Or run:
```bash
node scripts/get-linkedin-profile.js
```

## Step 6: Test the Connection

```bash
node scripts/test-linkedin.js
```

You're all set! 🚀
