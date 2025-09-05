"""
Daily reading hints and tips.

This module contains a collection of reading tips and hints to help users improve their reading habits.
"""

READING_HINTS = [
    # Reading Techniques
    "📖 **Reading Tip**: Try the 25-5 technique - read for 25 minutes, then take a 5-minute break. This helps maintain focus!",
    "👀 **Eye Care**: Remember the 20-20-20 rule - every 20 minutes, look at something 20 feet away for 20 seconds.",
    "🎯 **Focus Tip**: Find your optimal reading time. Are you a morning person or night owl? Read when you're most alert!",
    "📱 **Distraction-Free**: Put your phone in another room while reading. Out of sight, out of mind!",
    "🔍 **Active Reading**: Underline key points or take notes. This helps you remember and understand better.",
    "📚 **Book Selection**: Choose books that match your current mood and energy level. Don't force yourself to read something you're not enjoying.",
    "⏰ **Consistency**: Even 10 minutes of reading daily is better than 2 hours once a week. Build the habit!",
    "🌙 **Bedtime Reading**: Reading before bed can improve sleep quality and help you wind down naturally.",
    
    # Reading Environment
    "💡 **Lighting**: Natural light is best for reading. If using artificial light, make sure it's bright enough to avoid eye strain.",
    "🪑 **Comfort**: Find a comfortable reading spot. Good posture prevents neck and back pain during long reading sessions.",
    "🔇 **Quiet Space**: Create a dedicated reading space free from distractions. Your brain will associate this space with reading.",
    "☕ **Hydration**: Keep water nearby while reading. Staying hydrated helps maintain focus and concentration.",
    "🌡️ **Temperature**: A slightly cool room (around 68-72°F) is optimal for reading and concentration.",
    "🎵 **Background**: Some people read better with soft instrumental music, others prefer complete silence. Find what works for you.",
    
    # Reading Speed and Comprehension
    "⚡ **Speed Reading**: Don't worry about reading speed. Comprehension is more important than speed!",
    "🔄 **Re-reading**: It's okay to re-read difficult passages. Understanding is more important than finishing quickly.",
    "📝 **Summarize**: After each chapter, try to summarize the main points in your own words.",
    "🤔 **Question**: Ask yourself questions about what you're reading. This keeps your mind engaged.",
    "🔗 **Connect**: Try to connect what you're reading to your own experiences or other books you've read.",
    "📊 **Progress**: Track your reading progress. Seeing your progress can be very motivating!",
    
    # Reading Habits
    "📅 **Daily Goal**: Set a realistic daily reading goal. Even 10-20 pages a day adds up quickly!",
    "🎯 **Streak Building**: Focus on building a reading streak. Consistency is key to forming lasting habits.",
    "📚 **Variety**: Mix different types of books - fiction, non-fiction, biographies, etc. Variety keeps reading interesting.",
    "👥 **Book Clubs**: Consider joining a book club or reading group. Discussion enhances understanding and enjoyment.",
    "📖 **Bookmarks**: Use bookmarks to mark interesting passages you want to revisit later.",
    "🌟 **Favorites**: Keep a list of your favorite quotes or passages. You'll enjoy revisiting them later.",
    
    # Reading Challenges
    "🎲 **Genre Challenge**: Try reading a book from a genre you've never explored before.",
    "🌍 **Global Reading**: Read books by authors from different countries and cultures.",
    "📚 **Classics**: Don't be intimidated by classics. Start with shorter ones or modern translations.",
    "🔍 **Research**: If a book mentions something interesting, take a moment to research it further.",
    "💭 **Reflection**: After finishing a book, take time to reflect on what you learned or how it affected you.",
    "📝 **Reviews**: Write a brief review or rating of books you've read. This helps you remember them better.",
    
    # Reading Motivation
    "🏆 **Achievements**: Celebrate your reading milestones! Every book finished is an achievement.",
    "📈 **Progress**: Keep track of books read, pages read, or reading time. Progress is motivating!",
    "🎁 **Rewards**: Reward yourself after finishing a book or reaching a reading goal.",
    "👥 **Share**: Share interesting books or quotes with friends and family.",
    "📚 **Library**: Visit your local library regularly. The atmosphere can be very inspiring!",
    "🌟 **Inspiration**: Follow book blogs, podcasts, or social media accounts for reading inspiration.",
    
    # Reading Health
    "👁️ **Eye Health**: Take regular breaks to rest your eyes. Blink frequently while reading.",
    "🧘 **Posture**: Maintain good posture while reading. Use a book stand if reading for long periods.",
    "💪 **Hand Position**: Hold your book at a comfortable distance and angle to avoid strain.",
    "🔄 **Movement**: Stand up and stretch every 30-45 minutes of reading.",
    "💧 **Hydration**: Drink water regularly while reading to stay hydrated and focused.",
    "😴 **Sleep**: Don't sacrifice sleep for reading. A well-rested mind reads better!",
    
    # Reading Technology
    "📱 **E-readers**: E-readers can be great for travel and have adjustable lighting and font sizes.",
    "🔊 **Audiobooks**: Audiobooks are perfect for commuting, exercising, or when your eyes need a break.",
    "📚 **Digital vs Physical**: Both have benefits. Choose what works best for your situation and preferences.",
    "🔍 **Dictionary**: Keep a dictionary handy (or use your phone) to look up unfamiliar words.",
    "📝 **Note-taking**: Use apps or physical notebooks to take notes while reading.",
    "☁️ **Cloud Sync**: Use cloud services to sync your reading progress across devices.",
    
    # Reading Community
    "👥 **Book Discussions**: Join online book communities or forums to discuss books with others.",
    "📖 **Recommendations**: Ask friends, family, or librarians for book recommendations.",
    "🌟 **Reviews**: Read book reviews to help you choose your next read, but don't let them discourage you from trying something.",
    "🎯 **Challenges**: Participate in reading challenges or set personal reading goals.",
    "📚 **Sharing**: Share books you've enjoyed with others. Reading is more fun when shared!",
    "💬 **Discussion**: Talk about books with others. Different perspectives can enhance your understanding.",
    
    # Reading Goals
    "🎯 **SMART Goals**: Set Specific, Measurable, Achievable, Relevant, and Time-bound reading goals.",
    "📊 **Track Progress**: Use apps, spreadsheets, or journals to track your reading progress.",
    "🏆 **Milestones**: Celebrate reading milestones - first book, 10th book, 1000 pages, etc.",
    "📅 **Monthly Goals**: Set monthly reading goals that are challenging but achievable.",
    "🌟 **Yearly Goals**: Set annual reading goals and break them down into monthly targets.",
    "💪 **Stretch Goals**: Occasionally set stretch goals to push yourself beyond your comfort zone.",
]

def get_random_hint() -> str:
    """Get a random reading hint."""
    import random
    return random.choice(READING_HINTS)

def get_hint_by_category(category: str = None) -> str:
    """Get a hint by category (techniques, environment, habits, etc.)."""
    import random
    
    if category == "techniques":
        hints = [h for h in READING_HINTS if "📖" in h or "👀" in h or "🎯" in h or "📱" in h or "🔍" in h]
    elif category == "environment":
        hints = [h for h in READING_HINTS if "💡" in h or "🪑" in h or "🔇" in h or "☕" in h or "🌡️" in h]
    elif category == "habits":
        hints = [h for h in READING_HINTS if "📅" in h or "🎯" in h or "📚" in h or "👥" in h]
    elif category == "health":
        hints = [h for h in READING_HINTS if "👁️" in h or "🧘" in h or "💪" in h or "🔄" in h or "💧" in h or "😴" in h]
    elif category == "motivation":
        hints = [h for h in READING_HINTS if "🏆" in h or "📈" in h or "🎁" in h or "👥" in h or "📚" in h or "🌟" in h]
    else:
        hints = READING_HINTS
    
    return random.choice(hints) if hints else get_random_hint()
