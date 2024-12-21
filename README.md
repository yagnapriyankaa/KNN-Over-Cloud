# Secure and Controllable k-NN Computation over Cloud Using Homomorphic Encryption

## Introduction
Cloud computing has become an integral part of modern data storage and processing systems, offering unprecedented scalability and accessibility. However, the increasing reliance on cloud services raises concerns about the security and privacy of sensitive data. This project explores the application of homomorphic encryption to fortify cloud data security, with a specific focus on empowering secure and controllable k-nearest neighbors (k-NN) computation over the cloud.

Homomorphic encryption allows secure computations on encrypted data, ensuring that sensitive information remains confidential even during processing. The proposed solution aims to provide a robust framework for k-NN algorithms, enabling users to perform computations on encrypted data in the cloud without compromising the confidentiality of the underlying information.

---

## Problem Statement
The escalating migration of organizations to cloud platforms has underscored the imperative of safeguarding sensitive data during data-intensive tasks like k-nearest neighbors (k-NN) computations. Despite the prevalence of cloud security measures, existing solutions often fall short in ensuring both the confidentiality and controllability of data in the cloud. This project addresses this critical challenge by developing a practical application that leverages Paillier homomorphic encryption for secure and controllable k-NN computations over the cloud.

---

## Proposed System
The proposed system leverages the Paillier cryptosystem for secure data encryption in a cloud environment. The architecture involves:

- **Data Owner (DO):** Maintains a private database.
- **Cloud Server (CS):** Stores and processes encrypted data.
- **Query Users (QUs):** Submit encrypted queries.

The system ensures data privacy, query privacy, and key confidentiality while allowing efficient k-NN query processing over encrypted data. Key features include:
- Key generation.
- Database encryption.
- Query encryption.
- k-NN computation stages.

The design emphasizes security and efficiency within a semi-honest adversarial model.

---

## Features
- **Homomorphic Encryption:** Enables computations on encrypted data without decryption.
- **Secure k-NN Computation:** Performs privacy-preserving k-NN queries on the cloud.
- **Single-Round Communication:** Streamlined architecture compared to multi-round approaches.
- **Efficient and Scalable:** Suitable for cloud-based environments with large datasets.

---

## Steps to Run the Project

### 1. Programs Execution Order
Run the programs in the following order:
1. `cloud_server.py`
2. `data_owner.py`
3. `query_user.py`

### 2. Set Up the Cloud Server
Run the following commands in PowerShell in the directory `Final Project`:

```bash
docker build -t cloud-server .
docker run -p 65433:65433 cloud-server
```

### 3. Open the SageMath Environment
In two separate terminals, open the SageMath environment in the directory `Final Project` by running:

```bash
sage
```

### 4. Run `data_owner.py`
In one terminal, load and run the `data_owner.py` file:

```bash
load("data_owner.py")
```

Wait for the message in the Cloud Server's terminal:

```bash
[CLOUD SERVER]Encrypted query - q_dash Received
```

### 5. Run `query_user.py`
In the second terminal, load and run the `query_user.py` file:

```bash
load("query_user.py")
```

If successful, you will see the message in the query user's terminal:

```bash
Index Set : [3]
```

---

## Parameters That Can Be Changed

1. **Query:** Modify lines `126-129` in `query_user.py`.
2. **k (for k-NN computation):** Modify line `118` in `cloud_server.py`.
3. **Database:** Generate a new `database.txt` file using `data_gen.py` or use the provided example database.

---

## Software Requirements
- **Operating System:** Windows 8 or newer, Linux, macOS X v10.7 or newer
- **Programming Language:** Python
- **Software:** Docker
- **IDE:** VSCode

### Hardware Requirements
- **Processor:** Recommended 2GHz or more
- **Hard Drive:** Recommended 256GB or more
- **Memory (RAM):** Recommended 4GB or more

---

## Glossary
- **Cloud Computing:** Delivery of computing services over the internet.
- **Homomorphic Encryption:** Cryptographic technique enabling computations on encrypted data.
- **k-NN:** Machine learning algorithm used for classification and regression tasks.
- **Secure Computation:** Performing computations while maintaining data confidentiality.
- **Confidentiality:** Protecting sensitive information from unauthorized access.
- **Paillier Encryption System:** Enables secure computations on encrypted data without revealing sensitive information.

---

## References
1. [Homomorphic Encryption Overview](https://example.com/reference1)
2. [Paillier Cryptosystem](https://example.com/reference2)
3. [k-NN Algorithm](https://example.com/reference3)
