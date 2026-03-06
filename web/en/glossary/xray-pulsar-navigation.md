---
permalink: /en/glossary/xray-pulsar-navigation/
---

# X-ray Pulsar Navigation

> Author: [CislunarSpace](https://gitee.com/cislunarspace)
>
> Website: [https://cislunarspace.cn](https://cislunarspace.cn)

## 1 Basic Concepts of X-ray Pulsar Navigation

A pulsar is a highly spinning neutron star. When a star with more than 1.4 solar masses evolves to its late stage, significant consumption of its internal nuclear fuel leads to a sharp decrease in radiation pressure, which can no longer counterbalance gravity, resulting in a collapse that forms compact stars such as white dwarfs, neutron stars, and black holes [2]. Among these, a neutron star with a mass equivalent to the Sun has a diameter of approximately $10\mathrm{km}$, a core density reaching $10^{12}\mathrm{kg/cm}^3$, and a magnetic field strength of up to $10^4\sim10^{13}$ Gauss [3].

The rotation axis and magnetic axis of a pulsar are misaligned, and the two magnetic poles can emit radiation beams. As the star rotates and a magnetic pole beam sweeps across the detector, the detector receives a pulse signal — much like a lighthouse guiding ships at sea. The long-term stability of pulsar rotational periods is outstanding; the long-term stability of certain millisecond pulsars can rival that of current atomic clocks. Pulsars that emit radiation in the X-ray band are called X-ray pulsars. X-rays are high-energy radiation that can be detected by compact instruments, but they cannot penetrate the dense atmosphere of the Earth, so they can only be observed in outer space [4].

![Pulsar "Rotation" Model](./Figures/image.png)

By establishing a timing phase model of pulsars at the Solar System Barycenter (SSB), the arrival time of any pulse at the SSB can be predicted. Meanwhile, by on-orbit processing of photon measurement data, the arrival time of that pulse at the spacecraft can also be obtained. The difference between the measured time and the predicted time reflects the projection of the spacecraft's position relative to the SSB along the pulsar direction. By processing measurement information from different directions, the position and time of the spacecraft can be estimated. By comparing the pulsar bearing measurements with the pulsar direction vectors in inertial space, the attitude of the spacecraft body frame relative to the inertial frame can be determined.

As a type of celestial navigation, X-ray pulsar navigation shares the common features of celestial navigation: strong autonomy, strong anti-interference capability, high reliability, simultaneous positioning and attitude determination, and navigation errors that do not accumulate over time. In addition, X-ray pulsar navigation has unique advantages, mainly reflected in the following aspects:

(1) **Providing high-precision reference time standards.** The rotational period of X-ray pulsars is highly stable. For some millisecond pulsars, if the observation period exceeds 8 years, the long-term stability can reach the order of $10^{-15}$ [5]. Using pulsar observation information, one can maintain the spacecraft navigation system time by establishing an integrated pulsar time, and simultaneously calibrate the onboard atomic clock bias while determining the spacecraft position.

(2) **High navigation accuracy.** Traditional celestial navigation methods determine spacecraft positioning by measuring the spatial angle between reference celestial bodies and the spacecraft, and their accuracy depends on the distance from the spacecraft to the reference body. For deep space probes in the cruise phase, traditional celestial navigation methods can only achieve positioning accuracy of several thousand kilometers. However, under the same conditions, X-ray pulsar navigation accuracy can be better than ten kilometers.

Furthermore, compared with satellite navigation, X-ray pulsar navigation has the advantage of simultaneously serving both near-Earth spacecraft and deep space probes.

## 2 Research Progress on Pulsar Parameter Determination and Related Theory

Accurately determining the spatial distribution, radiation characteristics, and rotational period characteristics of X-ray pulsars is a prerequisite for conducting X-ray pulsar navigation research. The X-ray energy range emitted by pulsars is $0.1\sim200\,\text{keV}$ ($0.1\sim20\,\text{keV}$ for soft X-rays, $20\sim200\,\text{keV}$ for hard X-rays [6]). It is generally believed that soft X-rays are suitable for X-ray pulsar navigation. To make full use of existing ground-based and space-based observation resources, it is recommended to select pulsars that simultaneously emit radio signals (which can penetrate the atmosphere) and X-ray signals as navigation pulsars. Through ground-based radio observations, the spatial distribution and rotational period characteristics of pulsars can be determined; by launching spacecraft, the profile and phase information of pulsars in the X-ray band can be measured.

### 2.1 Discovery, Naming, and Classification of Pulsars

#### 2.1.1 Discovery of Pulsars

In 1967, graduate student Jocelyn Bell at the University of Cambridge, while analyzing interplanetary scintillation observation data, accidentally discovered a series of periodic signals in a direction with no known radio sources, and reported the finding to her supervisor, Professor Antony Hewish. Bell and Hewish initially speculated that these periodic signals might be messages from extraterrestrial beings. However, the pulse signals received by the research group only contained frequency shifts due to Earth's orbital motion, with no motion information from the source itself. Therefore, the signal source was ultimately confirmed to be an extraterrestrial natural body. In 1968, Hewish and Bell published the discovery in Nature, naming the discovered celestial radio source a "pulsar" [7]. The discovery of pulsars was one of the four major astronomical discoveries of the 1960s, opening up a new astronomical research field and profoundly impacting modern astrophysics. In 1974, Professor Hewish was awarded the Nobel Prize in Physics for the discovery of pulsars.

#### 2.1.2 Naming of Pulsars

Current pulsar names are expressed as "PSR reference_epoch pulsar_RA pulsar_Dec", where north declination is denoted by "$+$" and south declination by "$-$", with declination significant digits at $0.1^\circ$ or $0.01^\circ$. Therefore, the first pulsar discovered by Bell is named $\text{PSR}~1919+16$. Additionally, in some globular clusters where discovered pulsars have nearly identical positions, making them hard to distinguish by position alone, a letter is appended after the coordinates for differentiation. Similar to the position calibration of stars, the right ascension and declination of pulsars also need to account for the reference epoch. Older catalogs mostly use the Besselian year beginning as the epoch, denoted by $B$ (e.g., epoch $B~1900.0$, $B~1950.0$, etc.). The International Astronomical Union (IAU) stipulated that from $1984$ onward, catalogs should uniformly use the Julian year beginning as the epoch, denoted by $J$. The current standard is epoch $J~2000.0$. For pulsars discovered before $1993$, both epochs can be used, distinguished by $B$ and $J$ respectively. Pulsars discovered after $1993$ use only epoch $J$.

---

To be improved...

## References

[1] Wang Yidi. Research on X-ray Pulsar Signal Processing and Navigation Methods [D]. Changsha: National University of Defense Technology, 2016.

[2] Li Li. Research on Autonomous Navigation Methods for Spacecraft Based on X-ray Pulsars [D]. Changsha: National University of Defense Technology, 2007.

[3] Manchester R N, Hobbs G B, Teoh A, et al. The Australia telescope national facility pulsar catalogue [J]. Astronomical Journal, 2005, 129(4): 1993-2006.

[4] Zhu Cisheng. Astronomy Tutorial [M]. Beijing: Higher Education Press, 2003.

[5] Kaspi V M, Taylor J H, Ryba M F. High-precision timing of millisecond pulsars. III. Long-term monitoring of PSRs B1855+09 and B1937+21 [J]. Astrophysical Journal, 1994, 428: 713.

[6] Wang Shouxuan, Zhou Youyuan. X-ray Astrophysics [M]. Beijing: Science Press, 1999.

[7] Hewish A, Bell S J, Pilkington J D H, et al. Observation of a rapidly pulsating radio source [J]. Nature, 1968, 217(5130): 709-713.
