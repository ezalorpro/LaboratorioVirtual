tic
for i=1:10
sim('PIdf.slx')

t = salida.Time;
yout = salida.Data;
yc = controlador.Data;

subplot(2,1,1)
plot(t,yout)

subplot(2,1,2)
plot(t, yc)

end

toc/10
save('PIdf5', 't', 'yout', 'yc')
