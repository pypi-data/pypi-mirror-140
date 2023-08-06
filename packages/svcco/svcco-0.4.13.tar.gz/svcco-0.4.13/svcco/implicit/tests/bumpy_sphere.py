import numpy as np

def bumpy_sphere(samples=10,scale=5,a=3,b=1):
    data = np.zeros((samples**2,3))
    theta = np.linspace(0,2*np.pi,num=samples)
    phi = np.linspace(0,np.pi,num=samples)
    count = 0
    for t in theta:
        for p in phi:
            r = scale + np.cos(a*t)*np.sin(b*p)
            data[count,0] = r*np.cos(t)*np.sin(p)
            data[count,1] = r*np.sin(t)*np.sin(p)
            data[count,2] = r*np.cos(p)
            count += 1
    final_data = []
    for i in range(data.shape[0]):
        if i == 0:
            final_data.append(data[i,:])
            continue
        add = True
        for j in range(i):
            if np.all(np.isclose(data[i,:],data[j,:])):
                add = False
        if add:
            final_data.append(data[i,:])
    return np.array(final_data)
