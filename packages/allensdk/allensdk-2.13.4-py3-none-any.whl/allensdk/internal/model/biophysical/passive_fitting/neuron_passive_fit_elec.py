#!/usr/bin/env python

import allensdk.internal.model.biophysical.passive_fitting.neuron_utils as neuron_utils
import numpy as np
import os
import allensdk.core.json_utilities as json_utilities
from allensdk.model.biophys_sim.config import Config

# Load the morphology

BASEDIR = os.path.dirname(__file__)

@neuron_utils.read_neuron_fit_stdout
def neuron_passive_fit_elec(up_data,
                            down_data,
                            swc_path,
                            limit,
                            bridge,
                            elec_cap):
    h = neuron_utils.get_h()
    h.load_file("stdgui.hoc")
    h.load_file("import3d.hoc")
    neuron_utils.load_morphology(swc_path)

    for sec in h.allsec():
        sec.insert('pas')
        for seg in sec:
            seg.pas.e = 0

    h.load_file(os.path.join(BASEDIR, "passive", "fixnseg.hoc"))
    h.load_file(os.path.join(BASEDIR, "passive", "params.hoc"))
    h.load_file(os.path.join(BASEDIR, "passive", "circuit.ses"))
    h.load_file(os.path.join(BASEDIR, "passive", "mrf3.ses"))

    h.v_init = 0
    h.tstop = 100
    h.dt = 0.005

    fit_start = 4.0025

    circuit = h.LinearCircuit[0]
    circuit.R2 = bridge / 2.0
    circuit.R3 = bridge / 2.0
    circuit.C4 = elec_cap * 1e-3

    v_rec = h.Vector()
    t_rec = h.Vector()
    v_rec.record(h.soma[0](0.5)._ref_v)
    t_rec.record(h._ref_t)

    mrf = h.MulRunFitter[0]
    gen0 = mrf.p.pf.generatorlist.object(0)
    gen0.toggle()
    fit0 = gen0.gen.fitnesslist.object(0)

    up_t = h.Vector(up_data[:, 0])
    up_v = h.Vector(up_data[:, 1])
    fit0.set_data(up_t, up_v)
    fit0.boundary.x[0] = fit_start
    fit0.boundary.x[1] = limit
    fit0.set_w()

    gen1 = mrf.p.pf.generatorlist.object(1)
    gen1.toggle()
    fit1 = gen1.gen.fitnesslist.object(0)

    down_t = h.Vector(down_data[:, 0])
    down_v = h.Vector(down_data[:, 1])
    fit1.set_data(down_t, down_v)
    fit1.boundary.x[0] = fit_start
    fit1.boundary.x[1] = limit
    fit1.set_w()

    minerr = 1e12
    for _ in range(3):
        # Need to re-initialize the internal MRF variables, not top-level proxies
        # for randomize() to work
        mrf.p.pf.parmlist.object(0).val = 100
        mrf.p.pf.parmlist.object(1).val = 1
        mrf.p.pf.parmlist.object(2).val = 10000
        mrf.p.pf.putall()
        mrf.randomize()
        mrf.prun()
        if mrf.opt.minerr < minerr:
            fit_Ri = h.Ri
            fit_Cm = h.Cm
            fit_Rm = h.Rm
            minerr = mrf.opt.minerr

    h.region_areas()
    return {
        'Ri': fit_Ri,
        'Cm': fit_Cm,
        'Rm': fit_Rm,
        'err': minerr
        }

def main():
    import sys
    
    manifest_path = sys.argv[-1]
    elec_cap = float(sys.argv[-2])
    bridge = float(sys.argv[-3])
    limit = float(sys.argv[-4])
    os.chdir(os.path.dirname(manifest_path))
    app_config = Config()
    description = app_config.load(manifest_path)

    upfile = description.manifest.get_path('upfile')
    up_data =  np.loadtxt(upfile)
    downfile = description.manifest.get_path('downfile')
    down_data = np.loadtxt(downfile)
    swc_path = description.manifest.get_path('MORPHOLOGY')

    data = neuron_passive_fit_elec(up_data, down_data, swc_path, limit, bridge, elec_cap)

    output_file = description.manifest.get_path('fit_3_file')
    json_utilities.write(output_file, data)


if __name__ == '__main__': main()
