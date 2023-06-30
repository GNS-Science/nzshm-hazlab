import itertools
import numpy as np
import matplotlib.pyplot as plt

source_branches =  [

            {   "group": "Hik",
                "members" : [
                    {"tag": "Hik TL, N16.5, b0.95, C4, s0.42", "weight": 0.147216637218474, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjExNDQyOA==", "bg_id": "RmlsZToxMjY1MDI="},
                    {"tag": "Hik TL, N16.5, b0.95, C4, s1", "weight": 0.281154911079988, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjExNDQxNw==", "bg_id": "RmlsZToxMjY1MDQ="},
                    {"tag": "Hik TL, N16.5, b0.95, C4, s1.58", "weight": 0.148371277510384, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjExNDQyOQ==", "bg_id": "RmlsZToxMjY1MDY="},
                    {"tag": "Hik TL, N21.5, b1.097, C4, s0.42", "weight": 0.0887399956599006, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjExNDQyNA==", "bg_id": "RmlsZToxMjY1MDg="},
                    {"tag": "Hik TL, N21.5, b1.097, C4, s1", "weight": 0.169475991711261, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjExNDQxMw==", "bg_id": "RmlsZToxMjY1MTA="},
                    {"tag": "Hik TL, N21.5, b1.097, C4, s1.58", "weight": 0.0894359956258606, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjExNDQxNg==", "bg_id": "RmlsZToxMjY1MTI="},
                    {"tag": "Hik TL, N27.9, b1.241, C4, s0.42", "weight": 0.0192986223768806, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjExNDQxNA==", "bg_id": "RmlsZToxMjY1MTQ="},
                    {"tag": "Hik TL, N27.9, b1.241, C4, s1", "weight": 0.0368565846962387, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjExNDQwNg==", "bg_id": "RmlsZToxMjY1MTY="},
                    {"tag": "Hik TL, N27.9, b1.241, C4, s1.58", "weight": 0.019449984121013, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjExNDQwOQ==", "bg_id": "RmlsZToxMjY1MTg="},
                ]
            },

            {   "group": "PUY",
                "members" : [
                    {"tag": "Puy 0.7, N4.6, b0.902, C4, s0.28", "weight": 0.21, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjExODcxNw==", "bg_id": "RmlsZToxMjY1MjM="},
                    {"tag": "Puy 0.7, N4.6, b0.902, C4, s1", "weight": 0.52, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjExODcyMw==", "bg_id": "RmlsZToxMjY1MjQ="},
                    {"tag": "Puy 0.7, N4.6, b0.902, C4, s1.72", "weight": 0.27, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjExODcyOQ==", "bg_id": "RmlsZToxMjY1MjU="},
                ]
            },

             {   "group": "CRU",
                "members" : [
                    {"tag": "geodetic, TI, N2.7, b0.823 C4.2 s0.66", "weight": 0.0168335471189857, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyMDg5OA==", "bg_id": "RmlsZToxMjY0Nzc="},
                    {"tag": "geodetic, TI, N2.7, b0.823 C4.2 s1", "weight": 0.0408928149352719, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyMDkxMQ==", "bg_id": "RmlsZToxMjY0ODA="},
                    {"tag": "geodetic, TI, N2.7, b0.823 C4.2 s1.41", "weight": 0.0216771620919014, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyMDkwNA==", "bg_id": "RmlsZToxMjY0ODM="},
                    {"tag": "geodetic, TI, N3.4, b0.959 C4.2 s0.66", "weight": 0.0282427120823285, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyMDkxNw==", "bg_id": "RmlsZToxMjY0ODY="},
                    {"tag": "geodetic, TI, N3.4, b0.959 C4.2 s1", "weight": 0.0686084751056566, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyMDkwNg==", "bg_id": "RmlsZToxMjY0ODk="},
                    {"tag": "geodetic, TI, N3.4, b0.959 C4.2 s1.41", "weight": 0.0363691528229985, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyMDkwOA==", "bg_id": "RmlsZToxMjY0OTI="},
                    {"tag": "geodetic, TI, N4.6, b1.089 C4.2 s0.66", "weight": 0.00792374079868575, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyMDkxMw==", "bg_id": "RmlsZToxMjY0OTU="},
                    {"tag": "geodetic, TI, N4.6, b1.089 C4.2 s1", "weight": 0.0192487099590715, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyMDkxMg==", "bg_id": "RmlsZToxMjY0OTg="},
                    {"tag": "geodetic, TI, N4.6, b1.089 C4.2 s1.41", "weight": 0.0102036850851, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyMDkyNA==", "bg_id": "RmlsZToxMjY1MDE="},

                    {"tag": "geologic, TI, N2.7, b0.823 C4.2 s0.66", "weight": 0.0236560148670262, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyMDg4Ng==", "bg_id": "RmlsZToxMjY0Nzc="},
                    {"tag": "geologic, TI, N2.7, b0.823 C4.2 s1", "weight": 0.0574662625307477, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyMDg5Nw==", "bg_id": "RmlsZToxMjY0ODA="},
                    {"tag": "geologic, TI, N2.7, b0.823 C4.2 s1.41", "weight": 0.0304626983900857, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyMDg3NA==", "bg_id": "RmlsZToxMjY0ODM="},
                    {"tag": "geologic, TI, N3.4, b0.959 C4.2 s0.66", "weight": 0.0271169544446554, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyMDg5Mw==", "bg_id": "RmlsZToxMjY0ODY="},
                    {"tag": "geologic, TI, N3.4, b0.959 C4.2 s1", "weight": 0.0658737336745166, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyMDg4OQ==", "bg_id": "RmlsZToxMjY0ODk="},
                    {"tag": "geologic, TI, N3.4, b0.959 C4.2 s1.41", "weight": 0.0349194743556176, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyMDg3MQ==", "bg_id": "RmlsZToxMjY0OTI="},
                    {"tag": "geologic, TI, N4.6, b1.089 C4.2 s0.66", "weight": 0.00222703068831837, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyMDg4MQ==", "bg_id": "RmlsZToxMjY0OTU="},
                    {"tag": "geologic, TI, N4.6, b1.089 C4.2 s1", "weight": 0.00541000379473566, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyMDg5Mg==", "bg_id": "RmlsZToxMjY0OTg="},
                    {"tag": "geologic, TI, N4.6, b1.089 C4.2 s1.41", "weight": 0.00286782725429677, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyMDg4Mg==", "bg_id": "RmlsZToxMjY1MDE="},

                    {"tag": "geodetic, TD, N2.7, b0.823 C4.2 s0.66", "weight": 0.0168335471189857, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyMDk2NQ==", "bg_id": "RmlsZToxMjY0Nzc="},
                    {"tag": "geodetic, TD, N2.7, b0.823 C4.2 s1", "weight": 0.0408928149352719, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyMDk2Mw==", "bg_id": "RmlsZToxMjY0ODA="},
                    {"tag": "geodetic, TD, N2.7, b0.823 C4.2 s1.41", "weight": 0.0216771620919014, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyMDk1Ng==", "bg_id": "RmlsZToxMjY0ODM="},
                    {"tag": "geodetic, TD, N3.4, b0.959 C4.2 s0.66", "weight": 0.0282427120823285, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyMDk1Mw==", "bg_id": "RmlsZToxMjY0ODY="},
                    {"tag": "geodetic, TD, N3.4, b0.959 C4.2 s1", "weight": 0.0686084751056566, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyMDk2Nw==", "bg_id": "RmlsZToxMjY0ODk="},
                    {"tag": "geodetic, TD, N3.4, b0.959 C4.2 s1.41", "weight": 0.0363691528229985, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyMDk1NA==", "bg_id": "RmlsZToxMjY0OTI="},
                    {"tag": "geodetic, TD, N4.6, b1.089 C4.2 s0.66", "weight": 0.00792374079868575, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyMDk3Mw==", "bg_id": "RmlsZToxMjY0OTU="},
                    {"tag": "geodetic, TD, N4.6, b1.089 C4.2 s1", "weight": 0.0192487099590715, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyMDk1NQ==", "bg_id": "RmlsZToxMjY0OTg="},
                    {"tag": "geodetic, TD, N4.6, b1.089 C4.2 s1.41", "weight": 0.0102036850851, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyMDk3NA==", "bg_id": "RmlsZToxMjY1MDE="},

                    {"tag": "geologic, TD, N2.7, b0.823 C4.2 s0.66", "weight": 0.0236560148670263, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyMDkzNg==", "bg_id": "RmlsZToxMjY0Nzc="},
                    {"tag": "geologic, TD, N2.7, b0.823 C4.2 s1", "weight": 0.0574662625307477, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyMDkyNw==", "bg_id": "RmlsZToxMjY0ODA="},
                    {"tag": "geologic, TD, N2.7, b0.823 C4.2 s1.41", "weight": 0.0304626983900857, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyMDkzMg==", "bg_id": "RmlsZToxMjY0ODM="},
                    {"tag": "geologic, TD, N3.4, b0.959 C4.2 s0.66", "weight": 0.0271169544446554, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyMDk1MQ==", "bg_id": "RmlsZToxMjY0ODY="},
                    {"tag": "geologic, TD, N3.4, b0.959 C4.2 s1", "weight": 0.0658737336745166, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyMDk0NA==", "bg_id": "RmlsZToxMjY0ODk="},
                    {"tag": "geologic, TD, N3.4, b0.959 C4.2 s1.41", "weight": 0.0349194743556176, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyMDk0OA==", "bg_id": "RmlsZToxMjY0OTI="},
                    {"tag": "geologic, TD, N4.6, b1.089 C4.2 s0.66", "weight": 0.00222703068831837, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyMDkzNA==", "bg_id": "RmlsZToxMjY0OTU="},
                    {"tag": "geologic, TD, N4.6, b1.089 C4.2 s1", "weight": 0.00541000379473566, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyMDkzMQ==", "bg_id": "RmlsZToxMjY0OTg="},
                    {"tag": "geologic, TD, N4.6, b1.089 C4.2 s1.41", "weight": 0.00286782725429677, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyMDk0Mw==", "bg_id": "RmlsZToxMjY1MDE="},
                ]
             },



            {   "group": "SLAB",
                "members" : [
                    {"tag": "slab-uniform-1depth-rates", "weight":1.0,"inv_id":"", "bg_id":"RmlsZToxMjEwMzM="}
                ]
            }
        ]


gmm_branches =[
    [
        0.117,
        0.156,
        0.117,
        0.084,
        0.112,
        0.084,
        0.0198,
        0.0264,
        0.0198,
        0.0198,
        0.0264,
        0.0198,
        0.0198,
        0.0264,
        0.0198,
        0.0198,
        0.0264,
        0.0198,
        0.0198,
        0.0264,
        0.0198,
    ],
    [
        0.081,
        0.108,
        0.081,
        0.075,
        0.1,
        0.075,
        0.072,
        0.096,
        0.072,
        0.24,
    ],

    [
        0.084,
        0.112,
        0.084,
        0.075,
        0.1,
        0.075,
        0.069,
        0.092,
        0.069,
        0.24,
    ],

]

src_weight = []
for (hik, cru, slab) in itertools.product(
                                                source_branches[0]['members'],
                                                source_branches[2]['members'],
                                                source_branches[3]['members'] ):
    src_weight.append(hik['weight'] * cru['weight'] * slab['weight'])

gmm_weight = []
for (cru, interface, slab) in itertools.product(*gmm_branches):
    gmm_weight.append(cru*interface*slab)


total_weight = []
for src, gmm in itertools.product(src_weight, gmm_weight):
    total_weight.append(src*gmm)

total_weight = np.array(total_weight)
total_weight = np.flip(np.sort(total_weight))
cum_total_weight = np.cumsum(total_weight)

fig, ax = plt.subplots(1,3)
fig.set_size_inches(18,6)
fig.set_facecolor('white')
ax[0].plot(total_weight) 
ax[0].set_yscale('log')
ax[0].grid(color='lightgray')
ax[1].set_xscale('log')
# ax[0].ticklabel_format(axis='x', style='sci')
ax[0].set_xlabel('rank')
ax[0].set_ylabel('branch weight')


ax[1].plot(cum_total_weight) 
ax[1].set_xscale('log')
ax[1].grid(color='lightgray')
ax[1].set_xlabel('rank')
ax[1].set_ylabel('cumulative weight')



n, bins, patches = ax[2].hist(total_weight, bins=100, log=True, label='all branches')
ax[2].hist(total_weight[0:1000],bins=bins, log=True, label='first 1000 branches')
ax[2].set_xscale('log')
ax[2].set_xlabel('weight')
ax[2].legend()

plt.show()
