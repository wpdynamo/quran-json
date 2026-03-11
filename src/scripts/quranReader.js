export default function quranReader() {
  return {
    chapters: [],
    verses: [],
    selectedSurah: '',
    selectedReciter: '7',
    showTranslation: true,
    loading: false,
    isPlaying: false,
    playingIndex: -1,
    nowPlayingText: 'جاري التشغيل...',
    currentChapter: null,

    reciterMap: {
      '1': 'Abdul_Basit_Murattal_192kbps',
      '2': 'Abdurrahmaan_As-Sudais_192kbps',
      '3': 'Abdullah_Basfar_192kbps',
      '4': 'Abu_Bakr_Ash-Shaatree_128kbps',
      '5': 'Hani_Rifai_192kbps',
      '7': 'Alafasy_128kbps'
    },

    async loadChapters() {
      try {
        const res = await fetch('/assets/quran/chapters.json');
        this.chapters = await res.json();
      } catch (error) {
        console.error('Error loading chapters:', error);
      }
    },

    async loadSurah() {
      if (!this.selectedSurah) return;

      this.loading = true;
      this.verses = [];
      this.stopAudio();

      try {
        const surahNum = String(this.selectedSurah).padStart(3, '0');
        const res = await fetch(`/assets/quran/s${surahNum}.json`);
        this.verses = await res.json();
        this.currentChapter = this.chapters.find(ch => ch.id == this.selectedSurah);
      } catch (error) {
        console.error('Error loading surah:', error);
      } finally {
        this.loading = false;
      }
    },

    playVerse(index) {
      const verse = this.verses[index];
      const reciterFolder = this.reciterMap[this.selectedReciter] || 'Alafasy_128kbps';
      const paddedSurah = String(verse.s).padStart(3, '0');
      const paddedAyah = String(verse.a).padStart(3, '0');
      const verseAudioUrl = `https://everyayah.com/data/${reciterFolder}/${paddedSurah}${paddedAyah}.mp3`;

      const audio = this.$refs.audio;
      
      this.playingIndex = index;
      this.isPlaying = true;
      
      audio.src = verseAudioUrl;
      audio.play().catch(err => {
        console.error('Error playing audio:', err);
        alert('عذراً، حدث خطأ في تشغيل الصوت');
        this.isPlaying = false;
      });

      this.nowPlayingText = `الآية ${verse.a} من سورة ${this.currentChapter.name_arabic}`;

      setTimeout(() => {
        const verseEl = document.querySelector('.verse-container.playing');
        if (verseEl) {
          verseEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      }, 100);
    },

    stopAudio() {
      const audio = this.$refs.audio;
      audio.pause();
      audio.currentTime = 0;
      this.isPlaying = false;
      this.playingIndex = -1;
    },

    onAudioEnded() {
      if (this.playingIndex < this.verses.length - 1) {
        this.playVerse(this.playingIndex + 1);
      } else {
        this.stopAudio();
      }
    }
  };
}
