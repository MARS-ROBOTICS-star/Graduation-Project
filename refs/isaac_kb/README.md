# Isaac Knowledge Base

This directory stores local markdown conversions of the Isaac Sim and Isaac Lab manuals so they can be searched quickly in future work.

## Sources

- `/home/ubuntu/isaaclab_2.3.0_Full_Manual.pdf`
- `/home/ubuntu/IsaacSim_5.1_Full_Manual.pdf`

## Files

- `isaaclab_2.3.0_full_manual.md`
- `isaacsim_5.1_full_manual.md`

## Search Tips

- Search both manuals: `rg -n "keyword" /home/ubuntu/isaacsim/Graduation-Project/refs/isaac_kb`
- Search Isaac Lab only: `rg -n "keyword" /home/ubuntu/isaacsim/Graduation-Project/refs/isaac_kb/isaaclab_2.3.0_full_manual.md`
- Search Isaac Sim only: `rg -n "keyword" /home/ubuntu/isaacsim/Graduation-Project/refs/isaac_kb/isaacsim_5.1_full_manual.md`

## Refresh

Regenerate the markdown files with:

```bash
/home/ubuntu/miniconda3/bin/python3 /home/ubuntu/scripts/pdf_to_md.py /home/ubuntu/isaaclab_2.3.0_Full_Manual.pdf /home/ubuntu/isaacsim/Graduation-Project/refs/isaac_kb/isaaclab_2.3.0_full_manual.md --title "Isaac Lab 2.3.0 Full Manual"
/home/ubuntu/miniconda3/bin/python3 /home/ubuntu/scripts/pdf_to_md.py /home/ubuntu/IsaacSim_5.1_Full_Manual.pdf /home/ubuntu/isaacsim/Graduation-Project/refs/isaac_kb/isaacsim_5.1_full_manual.md --title "Isaac Sim 5.1 Full Manual"
```
