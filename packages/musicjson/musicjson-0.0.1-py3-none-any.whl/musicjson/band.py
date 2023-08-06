import numpy as np
import sounddevice as sd
import soundfile as sf
import json

def frequency(key):
    return 440 * (2 ** ((key - 49) / 12))

keys =['C','c','D','d','E','F','f','G','g','A','a','B']

piano_keys = {}
piano_keys['O']=0
for i in range(88):
    id = (i+9)%12
    octave = (i+9)//12
    key = keys[id]+str(octave)
    piano_keys[key] = frequency(i+1)
    # print(key,piano_keys[key])

def simple_ADSR(arr, adsr={'A':[0.1,1],
                           'D':[0.4,0.8],
                           'S':[0.7,0.8],
                           'R':[1,0]}):
    #check
    if adsr['R'][0]>adsr['S'][0]>adsr['D'][0]>adsr['A'][0] and adsr['R'][0]==1:
        l = len(arr)

        A_endid = int(l*adsr['A'][0])
        A_aplitude = adsr['A'][1]
        a = np.linspace(0,A_aplitude,A_endid)
        arr[:A_endid] = arr[:A_endid]*a

        D_endid = int(l*adsr['D'][0])
        D_aplitude = adsr['D'][1]
        d = np.linspace(A_aplitude,D_aplitude,D_endid-A_endid)
        arr[A_endid:D_endid] = arr[A_endid:D_endid] * d

        S_endid = int(l*adsr['S'][0])
        S_aplitude = adsr['S'][1]
        s = np.linspace(D_aplitude,S_aplitude,S_endid-D_endid)
        arr[D_endid:S_endid] = arr[D_endid:S_endid] * s

        R_endid = int(l*adsr['R'][0])
        R_aplitude = adsr['R'][1]
        r= np.linspace(S_aplitude,R_aplitude,R_endid-S_endid)
        arr[S_endid:R_endid] = arr[S_endid:R_endid] * r

        return arr

class Band:
    def __init__(self,sr=44100):
        self.sr = sr
        self.sin_amplitudes =list()

    def instrument(self,adsr={'A':[0.05,1],
                           'D':[0.1,0.9],
                           'S':[0.8,0.05],
                           'R':[1,0]},
                   mix={
        'sine':0.5,
        'square':0.2,
        'triangle':0.2,
        'saw':0.1}):
        self.adsr = adsr
        self.mix = mix

    def t_len(self,T):
        return np.linspace(0,T,int(self.sr*T))

    def sine_wav(self,fr,T):
        return np.sin(2*np.pi*fr*self.t_len(T))

    def sine_oct_wav(self,fr,T):
        wav =np.zeros(int(T*self.sr))
        count = 1
        for a in self.sin_amplitudes:
            wav +=a*self.sine_wav(fr*count,T)/count
            count+=1
        return simple_ADSR(wav,self.adsr)

    def square_wav(self,fr,T):
        wav = np.zeros(int(self.sr*T))
        for k in range(1,5):
            wav += 4/np.pi*np.sin(2*np.pi*(2*k-1)*fr*self.t_len(T))/(2*k-1)
        return wav

    def triangle_wav(self,fr,T):
        wav = np.zeros(int(self.sr*T))
        for k in range(1,5):
            wav += 8/(np.pi**2)*((-1)**k)*np.sin(2*np.pi*(2*k-1)*fr*self.t_len(T))/((2*k-1)**2)
        return wav

    def saw_wav(self,fr,T):
        wav = np.zeros(int(self.sr*T))
        for k in range(1,5):
            wav += 2/np.pi*((-1)**k)*np.sin(2*np.pi*k*fr*self.t_len(T))/k
        return wav

    def mixed_wav(self,fr=220,T=1):
        return simple_ADSR(self.sine_wav(fr,T)*self.mix['sine']+self.square_wav(fr,T)*self.mix['square']+self.triangle_wav(fr,T)*self.mix['triangle']+self.saw_wav(fr,T)*self.mix['saw'],self.adsr)

    def play(self,filename, save=False, savefile='saved.wav'):
        sr = self.sr
        inst = {
              "piano01": {
                "amplitudes": [1,0.0232,0.0757,0.0193,0.0199,0.0164,0.00153,0.000393,0.000150,0.000474],
                "ADSR": {
                  "A": [0.0532, 1],
                  "D": [0.285,0.1],
                  "S": [0.909,0.068],
                  "R": [1,0]
                }
              }
            }
        self.instrument(adsr=inst['piano01']['ADSR'], mix={'sine': 1, 'square': 0, 'triangle': 0, 'saw': 0})
        self.sin_amplitudes = inst['piano01']['amplitudes']

        print(f'reading the file {filename}... this may take some time...')
        with open(filename, 'r') as f:
            data = json.load(f)
        tempo = data['tempo']
        bds = data['band']
        notes = data['data'][0]
        wavs = np.array([])
        for note in notes:
            if isinstance(note[0], list):
                note_wav = np.zeros(int(note[1] / tempo * sr))
                for ns in note[0]:
                    note_wav += self.sine_oct_wav(fr=piano_keys[ns], T=note[1] / tempo)
                note_wav /= len(note[0])
            else:
                note_wav = self.sine_oct_wav(fr=piano_keys[note[0]], T=note[1] / tempo)

            wavs = np.append(wavs, note_wav)
        final = wavs

        self.instrument(adsr={
            'A': [0.2, 1],
            'D': [0.4, 0.95],
            'S': [0.8, 0.1],
            'R': [1, 0]
        }, mix={
            'sine': 0.1,
            'square': 0.1,
            'triangle': 0.8,
            'saw': 1})
        wavs = np.array([])
        for note in notes:
            if isinstance(note[0], list):
                note_wav = np.zeros(int(note[1] / tempo * sr))
                for ns in note[0]:
                    note_wav += self.mixed_wav(fr=piano_keys[ns], T=note[1] / tempo)
                wavs = np.append(wavs, note_wav / len(note[0]))
            else:
                wavs = np.append(wavs, self.mixed_wav(fr=piano_keys[note[0]], T=note[1] / tempo))
        # final = wavs
        final += wavs * 0.5
        final /= 1.5

        print(f'processing the data ...')
        for b in range(1, bds):
            notes = data['data'][b]
            wavs = np.array([])
            for note in notes:
                if isinstance(note[0], list):
                    note_wav = np.zeros(int(note[1] / tempo * sr))
                    for ns in note[0]:
                        note_wav += self.sine_oct_wav(fr=piano_keys[ns], T=note[1] / tempo)
                    note_wav /= len(note[0])
                else:
                    note_wav = self.sine_oct_wav(fr=piano_keys[note[0]], T=note[1] / tempo)

                wavs = np.append(wavs, note_wav)

            tmp = wavs

            self.instrument(adsr={
                'A': [0.2, 1],
                'D': [0.4, 0.95],
                'S': [0.8, 0.1],
                'R': [1, 0]
            }, mix={
                'sine': 0.1,
                'square': 0.1,
                'triangle': 0.2,
                'saw': 1})

            wavs = np.array([])
            for note in notes:
                if isinstance(note[0], list):
                    note_wav = np.zeros(int(note[1] / tempo * sr))
                    for ns in note[0]:
                        note_wav += self.mixed_wav(fr=piano_keys[ns], T=note[1] / tempo)
                    wavs = np.append(wavs, note_wav / len(note[0]))
                else:
                    wavs = np.append(wavs, self.mixed_wav(fr=piano_keys[note[0]], T=note[1] / tempo))

            tmp += wavs
            if final.shape[0] > tmp.shape[0]:
                tmp = np.append(tmp, np.zeros(final.shape[0] - tmp.shape[0]))
            elif final.shape[0] < tmp.shape[0]:
                final = np.append(final, np.zeros(tmp.shape[0] - final.shape[0]))
            final += tmp
            final /= 2

        if save:
            sf.write(savefile, final, sr, )
            print(f'saved to {savefile}')
        print(f'please enjoy your music...')
        sd.play(final, sr, blocking=True)
if __name__=='__main__':
    b = Band()
    b.play('Fur_Alice.json')
