import LinkedInService from '../services/linkedin.js';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const token = process.env.LINKEDIN_ACCESS_TOKEN;
  const userUrn = process.env.LINKEDIN_USER_ID;

  if (!token || !userUrn) {
    return res.status(500).json({ error: 'LinkedIn credentials not configured' });
  }

  try {
    const { text, imageUrl, altText } = req.body;

    if (!text) {
      return res.status(400).json({ error: 'Text content is required' });
    }

    const linkedin = new LinkedInService(token);

    let response;
    if (imageUrl) {
      response = await linkedin.postWithImage(text, imageUrl, userUrn, altText);
    } else {
      response = await linkedin.postTextUpdate(text, userUrn);
    }

    return res.status(200).json({
      success: true,
      postId: response.id,
      message: 'Post published to LinkedIn',
    });
  } catch (error) {
    console.error('LinkedIn posting error:', error);
    return res.status(500).json({
      error: error.message || 'Failed to post to LinkedIn',
    });
  }
}
