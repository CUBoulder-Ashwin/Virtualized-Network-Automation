# 🛰️ Virtualized Network Automation

Welcome to the **Virtualized Network Automation** project! This repository contains a modular Python-based automation system that integrates virtualization, containerization, and networking using modern technologies such as BGP, OpenStack, Docker, and SDN controllers.

---

## 📌 Summary

This lab demonstrates the full automation of network virtualization using a unified Python application. It integrates hypervisors, containers, and SDN technologies to dynamically create and configure virtual networks, virtual machines, and network services.

---

## 🧰 Required Technologies

- **BGP (Border Gateway Protocol)**
- **Hypervisor/Orchestrator** (e.g., OpenStack)
- **Docker Containers**
- **SDN Controller**
- **Hardware Server**
- **Service Chaining**

---

## 🎯 Objectives

Each objective is implemented as a **separate Python module** for a modular and scalable codebase. The main Python file (`main.py`) imports and integrates all modules.

### 1️⃣ Virtual Network Creation

- Automate creation of multiple Virtual Networks (VNs) using the hypervisor.
- Connect each VN to the public network.

### 2️⃣ VM Provisioning

- Automate creation of VMs in:
  - Single-tenant (same VN)
  - Multi-tenant (different VNs)
- Ensure VMs are accessible from the host server and can access the Internet.

### 3️⃣ Security Configuration

- Automate creation of security groups and port security rules.
- Enable both intra-VN and inter-VN communication.

### 4️⃣ BGP Router Automation

- Deploy a Quagga/FRR BGP router as a Docker container.
- Automate BGP peering configuration with the SDN controller.

### 5️⃣ SDN Controller Deployment

- Deploy an SDN controller as a Docker container.
- Configure BGP speaker to peer with the Quagga/FRR router.

---

## 📂 Check each folder for the respective README file.

