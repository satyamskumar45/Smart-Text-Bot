const SUPPORTED_LANGUAGES = [
  { code: "en", name: "English", emoji: "🇬🇧" },
  { code: "hi", name: "Hindi", emoji: "🇮🇳" },
  { code: "es", name: "Spanish", emoji: "🇪🇸" },
  { code: "fr", name: "French", emoji: "🇫🇷" },
  { code: "de", name: "German", emoji: "🇩🇪" },
  { code: "ja", name: "Japanese", emoji: "🇯🇵" },
];

const DAILY_WORDS = [
  {
    word: "Bonjour",
    language: "fr",
    meaning: "Hello",
    pronunciation: "bon-zhoor",
    example: "Bonjour! Comment ça va aujourd’hui?",
    tip: "Use this polite greeting for French conversation.",
  },
  {
    word: "Gracias",
    language: "es",
    meaning: "Thank you",
    pronunciation: "gra-thee-as",
    example: "Gracias por tu ayuda.",
    tip: "A simple thank-you used in everyday Spanish.",
  },
  {
    word: "Namaste",
    language: "hi",
    meaning: "Hello / Respectful greeting",
    pronunciation: "nah-mah-stay",
    example: "Namaste, aap kaise hain?",
    tip: "Common polite greeting in Hindi and South Asia.",
  },
  {
    word: "Danke",
    language: "de",
    meaning: "Thank you",
    pronunciation: "dahn-keh",
    example: "Danke für Ihren Einsatz.",
    tip: "Use when you want to express gratitude in German.",
  },
  {
    word: "ありがとう (Arigatou)",
    language: "ja",
    meaning: "Thank you",
    pronunciation: "ah-ree-gah-toh",
    example: "Arigatou gozaimasu.",
    tip: "A polite way to say thanks in Japanese.",
  },
  {
    word: "Hello",
    language: "en",
    meaning: "Hello",
    pronunciation: "heh-loh",
    example: "Hello! Welcome to Language Quest.",
    tip: "A universal opening greeting in English.",
  },
];

const QUIZ_QUESTIONS = [
  {
    language: "es",
    question: "What does ‘Gracias’ mean?",
    choices: ["Sorry", "Thank You", "Welcome", "Please"],
    answer: "Thank You",
    explanation: "Gracias is the Spanish word for thank you, used to show appreciation.",
  },
  {
    language: "fr",
    question: "What does ‘Bonjour’ mean?",
    choices: ["Good night", "Goodbye", "Hello", "Please"],
    answer: "Hello",
    explanation: "Bonjour is a French greeting meaning hello, especially used during the day.",
  },
  {
    language: "de",
    question: "What does ‘Guten Morgen’ mean?",
    choices: ["Good morning", "Good evening", "Thank you", "See you"],
    answer: "Good morning",
    explanation: "Guten Morgen is a German greeting used in the morning, meaning good morning.",
  },
  {
    language: "ja",
    question: "What does ‘Arigatou’ mean?",
    choices: ["Goodbye", "Please", "Thank you", "Excuse me"],
    answer: "Thank you",
    explanation: "Arigatou is a Japanese phrase meaning thank you in informal or polite contexts.",
  },
  {
    language: "hi",
    question: "What does ‘Namaste’ convey?",
    choices: ["Goodbye", "Hello / Respect", "Sorry", "Please"],
    answer: "Hello / Respect",
    explanation: "Namaste is a Hindi greeting used to say hello while showing respect.",
  },
  {
    language: "en",
    question: "What is the best translation for ‘Good evening’?",
    choices: ["Guten Morgen", "Buenas Noches", "Bonsoir", "Good evening"],
    answer: "Good evening",
    explanation: "Good evening is the English greeting used after sunset or late afternoon.",
  },
];

const VOCABULARY_WORDS = [
  {
    language: "fr",
    entries: [
      { word: "S'il vous plaît", meaning: "Please", pronunciation: "seel voo pleh", example: "Un café, s'il vous plaît." },
      { word: "Merci", meaning: "Thank you", pronunciation: "mehr-see", example: "Merci beaucoup." },
      { word: "Oui", meaning: "Yes", pronunciation: "wee", example: "Oui, j'aimerais ça." },
    ],
  },
  {
    language: "es",
    entries: [
      { word: "Por favor", meaning: "Please", pronunciation: "por fah-vor", example: "Pásame el agua, por favor." },
      { word: "Hola", meaning: "Hello", pronunciation: "oh-lah", example: "Hola, ¿cómo estás?" },
      { word: "Adiós", meaning: "Goodbye", pronunciation: "ah-dee-ohs", example: "Adiós, nos vemos mañana." },
    ],
  },
  {
    language: "de",
    entries: [
      { word: "Bitte", meaning: "Please / You're welcome", pronunciation: "bi-teh", example: "Bitte sprechen Sie langsamer." },
      { word: "Hallo", meaning: "Hello", pronunciation: "hah-loh", example: "Hallo! Wie geht's?" },
      { word: "Tschüss", meaning: "Bye", pronunciation: "chooss", example: "Tschüss und bis bald." },
    ],
  },
  {
    language: "ja",
    entries: [
      { word: "こんにちは (Konnichiwa)", meaning: "Hello", pronunciation: "kohn-nee-chee-wah", example: "こんにちは、元気ですか？" },
      { word: "お願いします (Onegaishimasu)", meaning: "Please", pronunciation: "oh-neh-gai-shee-mas", example: "メニューをお願いします。" },
      { word: "さようなら (Sayonara)", meaning: "Goodbye", pronunciation: "sah-yo-nah-rah", example: "さようなら、また会いましょう。" },
    ],
  },
  {
    language: "hi",
    entries: [
      { word: "धन्यवाद (Dhanyavaad)", meaning: "Thank you", pronunciation: "dhuh-nyuh-vahd", example: "धन्यवाद आपकी सहायता के लिए।" },
      { word: "कृपया (Kripya)", meaning: "Please", pronunciation: "kri-pya", example: "कृपया दरवाजा बंद करें।" },
      { word: "यहां", meaning: "Here", pronunciation: "yahaan", example: "कृपया यहाँ बैठें।" },
    ],
  },
  {
    language: "en",
    entries: [
      { word: "Welcome", meaning: "A greeting to someone new", pronunciation: "wel-kuhm", example: "Welcome to Language Quest!" },
      { word: "Practice", meaning: "To repeat for learning", pronunciation: "prak-tis", example: "Practice every day to build fluency." },
      { word: "Phrase", meaning: "A short group of words", pronunciation: "frayz", example: "Learn one phrase at a time." },
    ],
  },
];

const PHRASE_CATEGORIES = [
  {
    key: "greetings",
    label: "Greetings",
    phrases: [
      {
        text: "How are you?",
        translations: {
          es: "¿Cómo estás?",
          fr: "Comment ça va?",
          de: "Wie geht's?",
          ja: "お元気ですか？",
          hi: "आप कैसे हैं?",
          en: "How are you?",
        },
        pronunciation: {
          es: "koh-moh ehs-tahs",
          fr: "koh-mahn sah vah",
          de: "vee gates",
          ja: "o-genki desu ka",
          hi: "aap kaise hain",
          en: "how are you",
        },
        tip: "Use this to start a friendly conversation.",
      },
      {
        text: "Nice to meet you",
        translations: {
          es: "Mucho gusto",
          fr: "Enchanté",
          de: "Freut mich",
          ja: "はじめまして",
          hi: "आपसे मिलकर खुशी हुई",
          en: "Nice to meet you",
        },
        pronunciation: {
          es: "moo-choh goos-toh",
          fr: "ahn-shahn-tay",
          de: "froy-t mih",
          ja: "hajimemashite",
          hi: "aapse milkar khushi hui",
          en: "nice to meet you",
        },
        tip: "Great for introductions and first impressions.",
      },
    ],
  },
  {
    key: "travel",
    label: "Travel Basics",
    phrases: [
      {
        text: "Where is the train station?",
        translations: {
          es: "¿Dónde está la estación de tren?",
          fr: "Où se trouve la gare?",
          de: "Wo ist der Bahnhof?",
          ja: "駅はどこですか？",
          hi: "ट्रेन स्टेशन कहाँ है?",
          en: "Where is the train station?",
        },
        pronunciation: {
          es: "don-deh ehs-tah lah ehs-tah-syon de tren",
          fr: "oo suh troov lah gahr",
          de: "voh ist dare bahn-hof",
          ja: "eki wa doko desu ka",
          hi: "train station kahan hai",
          en: "where is the train station",
        },
        tip: "Use in transit hubs when asking for directions.",
      },
      {
        text: "Can I pay by card?",
        translations: {
          es: "¿Puedo pagar con tarjeta?",
          fr: "Puis-je payer par carte?",
          de: "Kann ich mit Karte zahlen?",
          ja: "カードで払えますか？",
          hi: "क्या मैं कार्ड से भुगतान कर सकता हूँ?",
          en: "Can I pay by card?",
        },
        pronunciation: {
          es: "pweh-doh pah-gar kon tar-heh-tah",
          fr: "pwee zhuh pay-ay par kart",
          de: "kahn ish mit kar-teh tsa-len",
          ja: "kaado de harae mas ka",
          hi: "kya main card se bhugtaan kar sakta hoon",
          en: "can I pay by card",
        },
        tip: "Useful for restaurant and checkout conversations.",
      },
    ],
  },
  {
    key: "interview",
    label: "Interview Phrases",
    phrases: [
      {
        text: "I am a quick learner.",
        translations: {
          es: "Aprendo rápido.",
          fr: "J'apprends vite.",
          de: "Ich lerne schnell.",
          ja: "私は早く学びます。",
          hi: "मैं जल्दी सीखता हूँ।",
          en: "I am a quick learner.",
        },
        pronunciation: {
          es: "ah-pren-doh rah-pee-doh",
          fr: "zhah-pron veet",
          de: "ikh lern-eh shnell",
          ja: "watashi wa hayaku manabimasu",
          hi: "main jaldi seekhta hoon",
          en: "I am a quick learner",
        },
        tip: "Perfect for sharing your strengths in a job interview.",
      },
      {
        text: "I enjoy working in a team.",
        translations: {
          es: "Disfruto trabajar en equipo.",
          fr: "J'aime travailler en équipe.",
          de: "Ich arbeite gerne im Team.",
          ja: "チームで働くのが好きです。",
          hi: "मुझे टीम में काम करना पसंद है।",
          en: "I enjoy working in a team.",
        },
        pronunciation: {
          es: "dees-froo-toh tra-bah-har en eh-kee-poh",
          fr: "zhem tra-vay-yay ahn eh-keep",
          de: "ikh ar-bai-teh gehr-neh im taym",
          ja: "chiimu de hataraku no ga suki desu",
          hi: "mujhe team mein kaam karna pasand hai",
          en: "I enjoy working in a team",
        },
        tip: "Use this to express collaboration skills.",
      },
    ],
  },
  {
    key: "business",
    label: "Business",
    phrases: [
      {
        text: "Can we schedule a call?",
        translations: {
          es: "¿Podemos programar una llamada?",
          fr: "Pouvons-nous planifier un appel?",
          de: "Können wir einen Anruf planen?",
          ja: "電話を予定できますか？",
          hi: "क्या हम कॉल शेड्यूल कर सकते हैं?",
          en: "Can we schedule a call?",
        },
        pronunciation: {
          es: "poh-deh-mohs pro-gra-mar oo-nah ya-mah-dah",
          fr: "poo-vohn noo plah-nee-fyay uh-nah-pel",
          de: "ker-nen veer eye-nen ahn-roof plah-nen",
          ja: "denwa wo yotei dekimasu ka",
          hi: "kya hum call schedule kar sakte hain",
          en: "Can we schedule a call",
        },
        tip: "Helpful when arranging meetings or follow-ups.",
      },
      {
        text: "I can share the agenda.",
        translations: {
          es: "Puedo compartir la agenda.",
          fr: "Je peux partager l'ordre du jour.",
          de: "Ich kann die Agenda teilen.",
          ja: "議題を共有できます。",
          hi: "मैं एजेंडा साझा कर सकता हूँ।",
          en: "I can share the agenda.",
        },
        pronunciation: {
          es: "pweh-doh kom-par-teer lah ah-hen-dah",
          fr: "zhuh puh par-tah-zhay lohr-druh doo zhoor",
          de: "ikh kann dee ah-gen-dah ty-len",
          ja: "gidai wo kyouyuu dekimasu",
          hi: "main agenda saajha kar sakta hoon",
          en: "I can share the agenda",
        },
        tip: "Use to gently propose a structure in business conversations.",
      },
    ],
  },
];

export {
  SUPPORTED_LANGUAGES,
  DAILY_WORDS,
  QUIZ_QUESTIONS,
  VOCABULARY_WORDS,
  PHRASE_CATEGORIES,
};
