#!/bin/bash

echo "Launching step 1 simulation..."
nohup python -u illumination.py led > illumination.log 2>&1 &
pid=$!
wait $pid
echo "Step 1 complete!"
python add_reflection.py
sed -i 's/np.array([(400,0.1), (1000,0.1)])/np.array([(400,1), (1000,1)])/g' optics.py
sed -i 's/detector_surface.set/#detector_surface.set/g' optics.py
nohup python -u simulation.py > simulation.log 2>&1 &
echo "Step 2 launched... You can leave the simulation running now."