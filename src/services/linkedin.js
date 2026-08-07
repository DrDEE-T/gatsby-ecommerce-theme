const https = require('https');

class LinkedInService {
  constructor(accessToken) {
    this.accessToken = accessToken;
    this.baseUrl = 'https://api.linkedin.com/v2';
  }

  async request(method, path, body = null) {
    return new Promise((resolve, reject) => {
      const url = new URL(this.baseUrl + path);
      const options = {
        hostname: url.hostname,
        port: 443,
        path: url.pathname + url.search,
        method,
        headers: {
          'Authorization': `Bearer ${this.accessToken}`,
          'Content-Type': 'application/json',
          'LinkedIn-Version': '202401',
        },
      };

      const req = https.request(options, (res) => {
        let data = '';
        res.on('data', (chunk) => {
          data += chunk;
        });
        res.on('end', () => {
          if (res.statusCode >= 400) {
            reject(new Error(`LinkedIn API error ${res.statusCode}: ${data}`));
          } else {
            try {
              resolve(data ? JSON.parse(data) : {});
            } catch (e) {
              resolve({});
            }
          }
        });
      });

      req.on('error', reject);

      if (body) {
        req.write(JSON.stringify(body));
      }
      req.end();
    });
  }

  async postTextUpdate(text, linkedInUrn) {
    const content = {
      author: linkedInUrn,
      lifecycleState: 'PUBLISHED',
      specificContent: {
        'com.linkedin.ugc.ShareContent': {
          shareCommentary: {
            text,
          },
          shareMediaCategory: 'NONE',
        },
      },
      visibility: {
        'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC',
      },
    };

    return this.request('POST', '/ugcPosts', content);
  }

  async postWithImage(text, imageUrl, linkedInUrn, altText = '') {
    const media = {
      title: {
        text: altText || 'Image',
      },
    };

    const registerResponse = await this.request('POST', '/assets?action=registerUpload', {
      registerUploadRequest: {
        recipes: ['urn:li:digitalmediaRecipe:feedshare-image'],
        owner: linkedInUrn,
        serviceRelationships: [
          {
            relationshipType: 'OWNER',
            identifier: 'urn:li:userGeneratedContent',
          },
        ],
      },
    });

    if (!registerResponse.value?.uploadMechanism) {
      throw new Error('Failed to register image upload');
    }

    const uploadUrl = registerResponse.value.uploadMechanism['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']?.uploadUrl;
    const assetId = registerResponse.value.asset;

    if (!uploadUrl || !assetId) {
      throw new Error('Missing upload URL or asset ID');
    }

    await this.uploadImage(uploadUrl, imageUrl);

    await this.request('POST', '/assets?action=finalizeUpload', {
      finalizeUploadRequest: {
        mediaArtifact: assetId,
      },
    });

    const content = {
      author: linkedInUrn,
      lifecycleState: 'PUBLISHED',
      specificContent: {
        'com.linkedin.ugc.ShareContent': {
          shareCommentary: {
            text,
          },
          shareMediaCategory: 'IMAGE',
          media: [
            {
              status: 'READY',
              media: assetId,
              ...media,
            },
          ],
        },
      },
      visibility: {
        'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC',
      },
    };

    return this.request('POST', '/ugcPosts', content);
  }

  async uploadImage(uploadUrl, imageUrl) {
    const imageBuffer = await this.fetchImageAsBuffer(imageUrl);

    return new Promise((resolve, reject) => {
      const url = new URL(uploadUrl);
      const options = {
        hostname: url.hostname,
        port: 443,
        path: url.pathname + url.search,
        method: 'PUT',
        headers: {
          'Content-Type': 'application/octet-stream',
          'Content-Length': imageBuffer.length,
        },
      };

      const req = https.request(options, (res) => {
        if (res.statusCode >= 400) {
          reject(new Error(`Image upload failed: ${res.statusCode}`));
        } else {
          resolve();
        }
      });

      req.on('error', reject);
      req.write(imageBuffer);
      req.end();
    });
  }

  async fetchImageAsBuffer(imageUrl) {
    return new Promise((resolve, reject) => {
      const url = new URL(imageUrl);
      const options = {
        hostname: url.hostname,
        port: 443,
        path: url.pathname + url.search,
        method: 'GET',
      };

      https.get(options, (res) => {
        const chunks = [];
        res.on('data', (chunk) => chunks.push(chunk));
        res.on('end', () => resolve(Buffer.concat(chunks)));
      }).on('error', reject);
    });
  }

  async getProfile() {
    return this.request('GET', '/me');
  }
}

module.exports = LinkedInService;
