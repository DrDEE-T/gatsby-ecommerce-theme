const fs = require('fs');
const path = require('path');
const LinkedInService = require('./linkedin');

const SCHEDULE_FILE = path.join(process.cwd(), '.linkedin-schedule.json');

class LinkedInScheduler {
  constructor(accessToken, userUrn) {
    this.linkedin = new LinkedInService(accessToken);
    this.userUrn = userUrn;
    this.schedule = this.loadSchedule();
  }

  loadSchedule() {
    if (fs.existsSync(SCHEDULE_FILE)) {
      return JSON.parse(fs.readFileSync(SCHEDULE_FILE, 'utf-8'));
    }
    return [];
  }

  saveSchedule() {
    fs.writeFileSync(SCHEDULE_FILE, JSON.stringify(this.schedule, null, 2));
  }

  addPost(text, options = {}) {
    const post = {
      id: Date.now().toString(),
      text,
      imageUrl: options.imageUrl || null,
      altText: options.altText || '',
      scheduledTime: options.scheduledTime || new Date().toISOString(),
      status: 'scheduled',
      createdAt: new Date().toISOString(),
    };

    this.schedule.push(post);
    this.saveSchedule();
    return post;
  }

  removePost(postId) {
    this.schedule = this.schedule.filter(p => p.id !== postId);
    this.saveSchedule();
  }

  async publishDuePost() {
    const now = new Date();
    const duePost = this.schedule.find(
      p =>
        p.status === 'scheduled' &&
        new Date(p.scheduledTime) <= now
    );

    if (!duePost) {
      return null;
    }

    try {
      const response = await this.linkedin.postTextUpdate(
        duePost.text,
        this.userUrn
      );

      duePost.status = 'published';
      duePost.publishedAt = new Date().toISOString();
      duePost.postId = response.id;
      this.saveSchedule();

      return { success: true, post: duePost };
    } catch (error) {
      duePost.status = 'failed';
      duePost.error = error.message;
      this.saveSchedule();

      return { success: false, post: duePost, error: error.message };
    }
  }

  async checkAndPublish() {
    const results = [];
    let published = true;

    while (published) {
      const result = await this.publishDuePost();
      if (result) {
        results.push(result);
      } else {
        published = false;
      }
    }

    return results;
  }

  listScheduled() {
    return this.schedule.filter(p => p.status === 'scheduled');
  }

  listPublished() {
    return this.schedule.filter(p => p.status === 'published');
  }

  getStats() {
    return {
      total: this.schedule.length,
      scheduled: this.schedule.filter(p => p.status === 'scheduled').length,
      published: this.schedule.filter(p => p.status === 'published').length,
      failed: this.schedule.filter(p => p.status === 'failed').length,
    };
  }
}

module.exports = LinkedInScheduler;
