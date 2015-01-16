from mpp.poe import normpdf
import scipy.stats


print(normpdf(20, 20, 10))



if __name__ == '__main__':
    x = np.linspace(-2, 2, 5)
    mu = np.array([[-3, 0, 3], [-2, -0.5, 2]])
    sigma = math.sqrt(1 - 0.7 ** 2)

    kernels1 = np.empty((mu.shape[0], mu.shape[1], x.shape[0]))
    for m in range(mu.shape[0]):
        for g in range(mu.shape[1]):
            kernels1[m, g] = scipy.stats.norm.pdf(x, mu[m, g], sigma)

    kernels2 = scipy.stats.norm.pdf(x,
                                    mu[:, :, np.newaxis],
                                    sigma)

    np.set_printoptions(formatter={'float': '{: 0.3f}'.format})
    print(kernels1)
    print(kernels2)

    # A = np.array([-1, 1, 1.5, 0, -1, -2, -0.5, 1.5])
    # print(scipy.stats.norm.ppf)
    # print(normpdf(x, mu=A, sigma=math.sqrt(1 - 0.7 ** 2)))