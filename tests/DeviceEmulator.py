
import numpy as np
import sys
sys.path.append('/home/nalbrecht/Bolt-Estimator/Bolt-robot---Estimator/src/python')
from Bolt_Utils import utils, Log
from TrajectoryGenerator import TrajectoryGenerator, Metal
from Graphics import Graphics
from Bolt_Filter_Complementary import ComplementaryFilter


'''
A Device Emulator class that emulates the device used in Bolt_Estimator
Send the estimator pseudo-data from IMU

'''


class DeviceEmulator():
    def __init__(self, TrajectoryGenerator, logger) -> None:
        # instant data to be fed to the estimator
        self.baseLinearAcceleration = np.zeros((3,))
        self.baseAngularVelocity = np.zeros((3,))
        self.baseOrientation = np.zeros((3,))
        self.q_mes = np.zeros((6,))
        self.v_mes = np.zeros((6,))

        self.generator = TrajectoryGenerator
        if logger is not None :
            self.logger = logger
            self.talkative = True
        else:
            self.talkative = False
        self.iter = 0
        if self.talkative : self.logger.LogTheLog("started Device Emulator")

        return None
    
    def GenerateTrajectory(self,N, NoiseLevelXY, NoiseLevelZ, Drift, NoiseLevelAttitude, T) -> None:
        # generate trajectories and attitudes that are supposed to look like real ones
        self.Traj = np.zeros((N, 3))
        self.Speed = np.zeros((N, 3))
        self.Acc = np.zeros((N, 3))
        self.AccG = np.zeros((N, 3))

        self.Theta = np.zeros((N, 3))
        self.Omega = np.zeros((N, 3))
        self.OmegaDot = np.zeros((N, 3))
        
        # TRAJ IN M, M/S, M/S²
        # generate X trajectory
        self.generator.Generate("sinus", NoiseLevel=NoiseLevelXY, N=N, amplitude=0.5, T=T, avgfreq=0.05)
        self.X, self.Xd, self.Xdd = self.generator.GetTrueTraj()
        self.XN, self.XNd, self.XNdd = self.generator.GetNoisyTraj()
        # generate Y trajectory
        self.generator.Generate("sinus", NoiseLevel=NoiseLevelXY, N=N, amplitude=0.1, T=T, avgfreq=0.05)
        self.Y, self.Yd, self.Ydd = self.generator.GetTrueTraj()
        self.YN, self.YNd, self.YNdd = self.generator.GetNoisyTraj()
        # generate Z trajectory
        self.generator.Generate("sinus", NoiseLevel=NoiseLevelZ, N=N, amplitude=0.01, T=T, avgfreq=0.5)
        self.Z, self.Zd, self.Zdd = self.generator.GetTrueTraj()
        self.ZN, self.ZNd, self.ZNdd = self.generator.GetNoisyTraj()


        # ATTITUDE IN RADIANS
        # data from generator are [[x0, x1, x2...]], removing 1D
        # generate X, Y attitude with noise and drift
        self.generator.Generate("sinus", NoiseLevel=NoiseLevelAttitude, N=N, amplitude=0.08, Drift=Drift, T=T, avgfreq=1.5)
        self.RX, self.RXd, self.RXdd = self.generator.GetTrueTraj()
        self.RXN, self.RXNd, self.RXNdd = self.generator.GetGyroTraj()
        # same traj without drift
        self.RXNnondrift,*o = self.generator.GetNoisyTraj()

        self.generator.Generate("sinus", NoiseLevel=NoiseLevelAttitude, N=N, amplitude=0.05, Drift=Drift, T=T, avgfreq=1.5)
        self.RY, self.RYd, self.RYdd = self.generator.GetTrueTraj()
        self.RYN, self.RYNd, self.RYNdd = self.generator.GetGyroTraj()
        self.RYNnondrift,*o = self.generator.GetNoisyTraj()
        # generate Z attitude
        self.generator.Generate("polynomial1", NoiseLevel=NoiseLevelAttitude/2, N=N, amplitude=0.3, Drift=Drift, T=T)
        self.RZ, self.RZd, self.RZdd = self.generator.GetTrueTraj()
        self.RZN, self.RZNd, self.RZNdd = self.generator.GetGyroTraj()

        # put all that noisy data in the right variables
        self.Traj[:, 0], self.Traj[:, 1], self.Traj[:, 2] = self.XN[0], self.YN[0], self.ZN[0]
        self.Speed[:, 0], self.Speed[:, 1], self.Speed[:, 2] = self.XNd[0], self.YNd[0], self.ZNd[0]
        self.Acc[:, 0], self.Acc[:, 1], self.Acc[:, 2] = self.XNdd[0], self.YNdd[0], self.ZNdd[0]

        self.Theta[:, 0], self.Theta[:, 1], self.Theta[:, 2] = self.RXN[0], self.RYN[0], self.RZN[0]
        self.Omega[:, 0], self.Omega[:, 1], self.Omega[:, 2] = self.RXNd[0], self.RYd[0], self.RZNd[0]
        self.OmegaDot[:, 0], self.OmegaDot[:, 1], self.OmegaDot[:, 2] = self.RXNdd[0], self.RYNdd[0], self.RZNdd[0]

        # acceleration with gravity (ADDED WITH NOISE BUT WITHOUT DRIFT)

        for j in range(N):
            self.AccG[j, :] = self.Acc[j, :] + utils.rotation( np.array([self.RXNnondrift[0, j], self.RYNnondrift[0, j], 0]), np.array([0, 0, 9.81]) )









    def LoadSimulatedData(self, Reader, kfile) -> None:
        # fetch .npy files
        Reader.AutoLoad(kfile, 'included')
        # base frame id
        base_id = 1
        
        # DATA THAT ESTIMATOR WILL NOT ACCESS
        # base acceleration
        self.Acc_true = Reader.A[:, base_id, :].copy
        self.AccG_true = Reader.A[:, base_id, :].copy
        n, _ = self.Acc_true.shape
        for j in range(n):
            glocal = Reader.Theta
            self.AccG_true += glocal

        # base rotation speed
        self.Omega_true = Reader.W[:, base_id, :].copy
        # base speed and attitude (IMU has an integrator)
        self.V_true = Reader.V[:, base_id, :].copy
        self.Theta_true = Reader.W[:, base_id, :].copy
        # encoders
        self.Q_true = Reader.Q
        # torques
        self.Tau_true = Reader.Tau




        # start noise generator
        noise = Metal(traj=self.Acc_True, NoiseLevel=0.5, DriftingCoeff=0.)
        

        # DATA THAT ESTIMATOR WILL ACCESS
        # base acceleration
        noise.SetNoise(NoiseLevel=0.5, DriftingCoeff=0.)
        self.Acc = noise.makeNoise(self.Acc_true)
        self.AccG = noise.makeNoise(self.Acc_true)
        # base rotation speed
        noise.SetNoise(NoiseLevel=0.5, DriftingCoeff=0.)
        self.Omega = noise.makeNoise(self.Omega_true)
        # base speed and attitude (IMU has an integrator)
        noise.SetNoise(NoiseLevel=0.5, DriftingCoeff=0.)
        self.V = noise.makeNoise(self.V_true)
        self.Theta = noise.makeNoise(self.Theta_true)
        # encoders
        noise.SetNoise(NoiseLevel=0.5, DriftingCoeff=0.)
        self.Q = noise.makeNoise(self.Q_true)
        # torques
        noise.SetNoise(NoiseLevel=0.5, DriftingCoeff=0.)
        self.Tau = noise.makeNoise(self.Tau_true)




        return None
    
    
    def Read(self):
        # iterate over the data as if it were real time, and get it ready to be provided to the estimator
        # estimator calls this method everytime

        self.baseLinearAcceleration = self.Acc[self.iter, :]
        self.baseLinearAccelerationGravity = self.AccG[self.iter, :]
        self.baseSpeed = self.Speed[self.iter, :]

        self.baseAngularVelocity = self.Omega[self.iter, :]
        self.baseOrientation = self.Theta[self.iter, :]
        self.q_mes = np.zeros((6,))
        self.v_mes = np.zeros((6,))

        self.offset_yaw_IMU = np.zeros(3)
        self.offset_speed_IMU = np.zeros(3)

        self.iter += 1
    
    def GetTranslation(self):
        # outputs data
        return self.Traj, self.Speed, self.Acc
    
    def GetRotation(self):
        # outputs data
        return self.Theta, self.Omega, self.OmegaDot

























