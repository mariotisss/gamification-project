# Advanced Gamification Features

While the core gamification loop handles fundamental User, Mission, and Reward CRUD operations (along with GitHub integrations and basic titles/daily missions), this document outlines the **advanced gamification mechanics** intended to deepen engagement, foster collaboration, and provide long-term progression.

These features will eventually be incorporated into the Hexagonal Architecture domains (`/gamification-system/domain/entities`).

## 1. Progression & Economy

### Dual-Currency System
To separate pure progression from cosmetic purchasing power, the system implements two distinct metrics:
- **Experience Points (XP):** The primary metric indicating a user's overall progress and level. XP cannot be spent; it is strictly cumulative.
- **DevCoins (Spendable Economy):** A virtual currency awarded alongside XP for completing missions. Users can spend DevCoins in a virtual "Shop" to purchase:
  - Custom avatars and profile borders.
  - "Streak Freeze" items to protect their daily login/commit streaks.
  - Temporary UI themes or badges.

### Skill Trees
Rather than a single, generic leveling track, progress is categorized into specific skill domains based on the type of work performed. This allows users to specialize and showcase their unique strengths:
- **Mentor Tree:** Leveled up by reviewing PRs, approving code, and answering internal questions.
- **Infrastructure Tree:** Leveled up by closing DevOps/SRE-related issues, deploying to production, or optimizing infrastructure.
- **Feature Builder Tree:** Leveled up by merging feature branches or resolving user-facing tickets.

## 3. Social & Competitive

### Weekly/Monthly Resets
To prevent older, highly leveled users from dominating the all-time leaderboards indefinitely, the system will implement time-boxed competitive cycles:
- **Weekly/Monthly Leaderboards:** Leaderboards reset every week/month, giving everyone a fresh chance to rank highly.
- **Leagues System (e.g., Bronze, Silver, Gold):** Users are grouped into leagues. Finishing in the top 10% of a league at the end of the month promotes the user to the next tier, providing a continuous challenge.

### Guilds / Squads (Co-op)
To foster teamwork and reduce toxic individual competition, users can form or join groups:
- **Guild Missions:** Objectives that require combined effort (e.g., "The squad must review 30 PRs this sprint").
- **Collective Rewards:** Completing Guild Missions yields highly sought-after rewards (large XP bonuses, unique squad badges) that are distributed to all contributing members.

### Peer-to-Peer Kudos / Bounties
Encouraging peer-to-peer recognition and assistance:
- **Kudos:** Users receive a weekly allowance of "Kudos" points to award to colleagues who have been exceptionally helpful.
- **Bounties:** A user stuck on a difficult Jira/Linear ticket can spend their own DevCoins to place a "Bounty" on the task, incentivizing peers to assist them in resolving the issue.

## 4. Expansion Integrations

### Chatbot (Slack/Discord)
To ensure achievements are recognized publicly and build hype within the team:
- A dedicated bot connects the gamification backend to company communication channels.
- **Broadcasts:** Automatically announces major milestones, legendary badge unlocks, leveling up, or the completion of incredibly difficult continuous streaks in a public channel.

## 5. Feedback & Summaries

### Developer "Wrapped"
Taking inspiration from popular end-of-year summaries (like Spotify Wrapped):
- **Automated Summaries:** Generates a personalized, highly visual summary at the end of the month or year.
- **Metrics Displayed:** Showcases their unique stats, such as lines of code reviewed, most frequently used programming languages, top achievements unlocked, and their overall ranking progression.
