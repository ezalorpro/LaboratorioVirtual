numerador = [1, 2];
denominador = [1 0.5 3];

Gs = tf(numerador, denominador, 'InputDelay', 1.5);
Gsx = pade(Gs,4);

[Step_y, Step_t] = step(Gs, 35);
[Impulse_y, Impulse_t] = impulse(Gs, 35);
[MagB, PhaB, FreqB] = bode(Gs);
[GM, GP, Wg, Wp] = margin(Gs);
[Re,Img,FreqN] = nyquist(Gs);
[r, k] = rlocus(Gsx);
[MagN, PhaN, WN] = nichols(Gs);


GM = mag2db(GM);
MagB = mag2db(MagB);
MagN = mag2db(MagN);

figure(1)
plot(Step_t, Step_y)
grid()

figure(2)
plot(Impulse_t, Impulse_y)
grid()

figure(3)
semilogx(FreqB, squeeze(MagB))
grid()

figure(4)
semilogx(FreqB, squeeze(PhaB))
grid()

figure(5)
plot(squeeze(Re), squeeze(Img),squeeze(Re), squeeze(-Img))
grid()

figure(6)
index = size(r);
for i=1:index(1)
    plot(real(r(i,:)), imag(r(i,:)))
    hold on
end
grid()
hold off

figure(7)
plot(squeeze(PhaN), squeeze(MagN))
grid()

SciFreqB = FreqB;
SciFreqN = FreqN;
SciWN = WN;

set = 'S3';
save(strcat(set,'Step'),'Step_t','Step_y')
save(strcat(set,'Imp'),'Impulse_y','Impulse_t')
save(strcat(set,'Bode'),'MagB','PhaB','FreqB')
save(strcat(set,'Margin'),'GM','GP','Wg','Wp')
save(strcat(set,'Nyquist'),'Re','Img','FreqN')
save(strcat(set,'Rlocus'),'r','k')
save(strcat(set,'Nichols'),'MagN','PhaN','WN')
save(strcat(set,'Freq'),'SciFreqB', 'SciFreqN', 'SciWN')