# Прогон `E2/heading_2000`

## Параметры

- `collection`: k8s__multilingual-e5-base__heading-2000-0-h
- `embedding_model`: multilingual-e5-base
- `chunking.strategy`: heading
- `chunking.chunk_size`: 2000
- `chunking.chunk_overlap`: 0
- `chunking.include_heading`: True
- `reranker`: True
- `candidates`: 20
- `score_threshold`: 0.78
- `dedup_threshold`: 0.8
- `min_chars`: 50
- `rerank_min_score`: 0.1
- `max_per_document`: 0
- `top_k`: 5
- `questions`: 40

## Retrieval (32 вопросов с ответом)

| K | Hit@K | Recall@K | Precision@K |
|--:|--:|--:|--:|
| 1 | 0.812 | 0.750 | 0.812 |
| 3 | 1.000 | 0.984 | 0.698 |
| 5 | 1.000 | 1.000 | 0.619 |
| 10 | 1.000 | 1.000 | 0.571 |
| 20 | 1.000 | 1.000 | 0.544 |

MRR: **0.901**

| Тип | Hit@5 | Recall@5 | MRR |
|---|--:|--:|--:|
| фактологические | 1.000 | 1.000 | 1.000 |
| поиск конкретики | 1.000 | 1.000 | 0.875 |
| по нескольким документам | 1.000 | 1.000 | 0.762 |
| понимание контекста | 1.000 | 1.000 | 0.929 |

Вопросы без ответа: контекст отсечён фильтрами в 75% случаев.
Вопросы с ответом: контекст отсечён целиком в 0% случаев.

Средняя задержка: retrieval 0.3696 с

## По вопросам

| id | Тип | Hit@5 | RR | Отказ | Correctness | Faithfulness |
|---|---|--:|--:|:-:|:-:|:-:|
| f01 | фактологические | 1.000 | 1.000 | — | — | — |
| f02 | фактологические | 1.000 | 1.000 | — | — | — |
| f03 | фактологические | 1.000 | 1.000 | — | — | — |
| f04 | фактологические | 1.000 | 1.000 | — | — | — |
| f05 | фактологические | 1.000 | 1.000 | — | — | — |
| f06 | фактологические | 1.000 | 1.000 | — | — | — |
| f07 | фактологические | 1.000 | 1.000 | — | — | — |
| f08 | фактологические | 1.000 | 1.000 | — | — | — |
| f09 | фактологические | 1.000 | 1.000 | — | — | — |
| f10 | фактологические | 1.000 | 1.000 | — | — | — |
| s01 | поиск конкретики | 1.000 | 1.000 | — | — | — |
| s02 | поиск конкретики | 1.000 | 0.500 | — | — | — |
| s03 | поиск конкретики | 1.000 | 1.000 | — | — | — |
| s04 | поиск конкретики | 1.000 | 1.000 | — | — | — |
| s05 | поиск конкретики | 1.000 | 0.500 | — | — | — |
| s06 | поиск конкретики | 1.000 | 1.000 | — | — | — |
| s07 | поиск конкретики | 1.000 | 1.000 | — | — | — |
| s08 | поиск конкретики | 1.000 | 1.000 | — | — | — |
| m01 | по нескольким документам | 1.000 | 0.333 | — | — | — |
| m02 | по нескольким документам | 1.000 | 0.500 | — | — | — |
| m03 | по нескольким документам | 1.000 | 1.000 | — | — | — |
| m04 | по нескольким документам | 1.000 | 1.000 | — | — | — |
| m05 | по нескольким документам | 1.000 | 1.000 | — | — | — |
| m06 | по нескольким документам | 1.000 | 0.500 | — | — | — |
| m07 | по нескольким документам | 1.000 | 1.000 | — | — | — |
| c01 | понимание контекста | 1.000 | 1.000 | — | — | — |
| c02 | понимание контекста | 1.000 | 1.000 | — | — | — |
| c03 | понимание контекста | 1.000 | 1.000 | — | — | — |
| c04 | понимание контекста | 1.000 | 1.000 | — | — | — |
| c05 | понимание контекста | 1.000 | 1.000 | — | — | — |
| c06 | понимание контекста | 1.000 | 0.500 | — | — | — |
| c07 | понимание контекста | 1.000 | 1.000 | — | — | — |
| n01 | нет в базе | — | — | — | — | — |
| n02 | нет в базе | — | — | — | — | — |
| n03 | нет в базе | — | — | — | — | — |
| n04 | нет в базе | — | — | — | — | — |
| n05 | нет в базе | — | — | — | — | — |
| n06 | нет в базе | — | — | — | — | — |
| n07 | нет в базе | — | — | — | — | — |
| n08 | нет в базе | — | — | — | — | — |

## Подробно

### f01 — фактологические

**Вопрос:** Что такое Pod?

**Эталон:** Pod — наименьшая развёртываемая единица вычислений в Kubernetes, группа из одного или нескольких контейнеров с общими хранилищем и сетевыми ресурсами и спецификацией их запуска.

**Релевантные документы (any):** `concepts/workloads/pods/_index.md`

**Найдено (top-5 из 18):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 18 → final 18
1. ✓ `concepts/workloads/pods/_index.md` — Pods (score 0.840, rerank 0.999)
2.   `tutorials/kubernetes-basics/explore/explore-intro.md` — Viewing Pods and Nodes > Kubernetes Pods (score 0.816, rerank 0.994)
3. ✓ `concepts/workloads/pods/_index.md` — Pods > What is a Pod? (score 0.802, rerank 0.991)
4. ✓ `concepts/workloads/pods/_index.md` — Pods > What's next (score 0.803, rerank 0.970)
5. ✓ `concepts/workloads/pods/_index.md` — Pods > Working with Pods (score 0.798, rerank 0.965)

### f02 — фактологические

**Вопрос:** Какой компонент control plane хранит все данные кластера?

**Эталон:** etcd — согласованное высокодоступное хранилище «ключ-значение» для всех данных API-сервера.

**Релевантные документы (any):** `concepts/overview/components.md`

**Найдено (top-5 из 12):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 12 → final 12
1. ✓ `concepts/overview/components.md` — Kubernetes Components > Core Components > Control Plane Components (score 0.823, rerank 0.961)
2.   `tutorials/kubernetes-basics/create-cluster/cluster-intro.md` — Using Minikube to Create a Cluster > Kubernetes Clusters > Cluster Diagram (score 0.795, rerank 0.888)
3.   `tasks/administer-cluster/kubeadm/kubeadm-reconfigure.md` — Reconfiguring a kubeadm cluster > Persisting the reconfiguration > Persisting Node object reconfiguration > Persisting control plane component reconfiguration (score 0.804, rerank 0.825)
4.   `concepts/security/multi-tenancy.md` — Multi-tenancy > Implementations > Virtual control plane per tenant (score 0.799, rerank 0.816)
5.   `concepts/architecture/_index.md` — Cluster Architecture > Control plane components (score 0.818, rerank 0.815)

### f03 — фактологические

**Вопрос:** Какой порт обычно использует HTTP API kubelet на рабочих узлах?

**Эталон:** TCP-порт 10250.

**Релевантные документы (any):** `concepts/security/api-server-bypass-risks.md`

**Найдено (top-5 из 11):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 19 → rerank 11 → final 11
1. ✓ `concepts/security/api-server-bypass-risks.md` — Kubernetes API Server Bypass Risks > The kubelet API (score 0.848, rerank 0.996)
2.   `tutorials/cluster-management/kubelet-standalone.md` — Running Kubelet in Standalone Mode > Download, install, and configure the components > Download and set up the kubelet (score 0.823, rerank 0.935)
3.   `concepts/architecture/control-plane-node-communication.md` — Communication between Nodes and the Control Plane > Node to Control Plane (score 0.831, rerank 0.898)
4.   `concepts/security/controlling-access.md` — Controlling Access to the Kubernetes API > Transport security (score 0.847, rerank 0.760)
5.   `tutorials/cluster-management/kubelet-standalone.md` — Running Kubelet in Standalone Mode > Run a Pod in the kubelet > Find out information about the kubelet and the Pod (score 0.829, rerank 0.658)

### f04 — фактологические

**Вопрос:** Из какого диапазона по умолчанию выделяются порты для Service типа NodePort?

**Эталон:** Из диапазона 30000–32767.

**Релевантные документы (any):** `concepts/services-networking/service.md`

**Найдено (top-5 из 12):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 12 → final 12
1. ✓ `concepts/services-networking/service.md` — Service > Service type > `type: NodePort` (score 0.837, rerank 0.992)
2. ✓ `concepts/services-networking/service.md` — Service > Service type > `type: NodePort` > Reserve Nodeport ranges to avoid collisions (score 0.847, rerank 0.992)
3. ✓ `concepts/services-networking/service.md` — Service > Service type > `type: NodePort` > Choosing your own port (score 0.824, rerank 0.947)
4.   `tasks/access-application-cluster/create-external-load-balancer.md` — Create an External Load Balancer > Preserving the client source IP (score 0.810, rerank 0.797)
5.   `tutorials/services/source-ip.md` — Using Source IP > Source IP for Services with `Type=NodePort` (score 0.805, rerank 0.706)

### f05 — фактологические

**Вопрос:** Что делает kube-scheduler?

**Эталон:** Отслеживает Pod'ы, ещё не назначенные на узел, и выбирает для каждого из них подходящий узел.

**Релевантные документы (any):** `concepts/overview/components.md`, `concepts/scheduling-eviction/kube-scheduler.md`

**Найдено (top-5 из 19):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 19 → final 19
1. ✓ `concepts/scheduling-eviction/kube-scheduler.md` — Kubernetes Scheduler > kube-scheduler (score 0.864, rerank 0.999)
2.   `concepts/scheduling-eviction/scheduler-perf-tuning.md` — Scheduler Performance Tuning (score 0.863, rerank 0.996)
3. ✓ `concepts/scheduling-eviction/kube-scheduler.md` — Kubernetes Scheduler > kube-scheduler > Node selection in kube-scheduler (score 0.842, rerank 0.993)
4.   `concepts/extend-kubernetes/_index.md` — Extending Kubernetes > Scheduling extensions (score 0.865, rerank 0.987)
5.   `concepts/scheduling-eviction/scheduler-perf-tuning.md` — Scheduler Performance Tuning > Node scoring threshold (score 0.831, rerank 0.984)

### f06 — фактологические

**Вопрос:** Какое значение restartPolicy у Pod используется по умолчанию?

**Эталон:** Always.

**Релевантные документы (any):** `concepts/workloads/pods/pod-lifecycle.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 20 → final 20
1. ✓ `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > How Pods handle problems with containers > Container restarts > Pod-level container restart policy (score 0.869, rerank 0.995)
2.   `concepts/workloads/pods/_index.md` — Pods > Pods with multiple containers (score 0.843, rerank 0.984)
3. ✓ `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > How Pods handle problems with containers > Container restarts > Restart All Containers > How in-place Pod restarts work (score 0.863, rerank 0.978)
4. ✓ `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > How Pods handle problems with containers > Container restarts > Pod-level container restart policy > Restart behavior comparison (score 0.858, rerank 0.969)
5. ✓ `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > How Pods handle problems with containers > Container restarts > Pod-level container restart policy > Sidecar containers and restart policies (score 0.862, rerank 0.928)

### f07 — фактологические

**Вопрос:** Какой максимальный объём данных можно хранить в одном ConfigMap?

**Эталон:** Не более 1 MiB.

**Релевантные документы (any):** `concepts/configuration/configmap.md`

**Найдено (top-5 из 8):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 8 → final 8
1. ✓ `concepts/configuration/configmap.md` — ConfigMaps > Motivation (score 0.826, rerank 0.989)
2. ✓ `concepts/configuration/configmap.md` — ConfigMaps > ConfigMaps and Pods (score 0.805, rerank 0.519)
3.   `concepts/storage/volumes.md` — Volumes > Types of volumes > configMap (score 0.804, rerank 0.393)
4.   `tasks/configure-pod-container/configure-pod-configmap.md` — Configure a Pod to Use a ConfigMap > Understanding ConfigMaps and Pods (score 0.797, rerank 0.328)
5.   `tutorials/configuration/configure-redis-using-configmap.md` — Configuring Redis using a ConfigMap > Real World Example: Configuring Redis using a ConfigMap (score 0.797, rerank 0.288)

### f08 — фактологические

**Вопрос:** Для чего в Kubernetes нужны Namespace?

**Эталон:** Namespace — механизм изоляции групп ресурсов внутри одного кластера; имена ресурсов должны быть уникальны в пределах namespace, но не между namespace.

**Релевантные документы (any):** `concepts/overview/working-with-objects/namespaces.md`

**Найдено (top-5 из 14):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 14 → final 14
1. ✓ `concepts/overview/working-with-objects/namespaces.md` — Namespaces > When to Use Multiple Namespaces (score 0.858, rerank 0.990)
2.   `concepts/security/multi-tenancy.md` — Multi-tenancy > Control plane isolation > Namespaces (score 0.862, rerank 0.988)
3. ✓ `concepts/overview/working-with-objects/namespaces.md` — Namespaces (score 0.865, rerank 0.974)
4.   `tasks/administer-cluster/namespaces.md` — Share a Cluster with Namespaces > Understanding the motivation for using namespaces (score 0.842, rerank 0.956)
5.   `tutorials/cluster-management/namespaces-walkthrough.md` — Namespaces Walkthrough (score 0.853, rerank 0.895)

### f09 — фактологические

**Вопрос:** Что означает фаза Pending у Pod?

**Эталон:** Pod принят кластером, но один или несколько контейнеров ещё не готовы к запуску — в том числе Pod ждёт планирования на узел или загрузки образов.

**Релевантные документы (any):** `concepts/workloads/pods/pod-lifecycle.md`

**Найдено (top-5 из 12):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 12 → final 12
1. ✓ `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > Pod phase (score 0.840, rerank 0.994)
2. ✓ `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle (score 0.826, rerank 0.963)
3.   `tasks/debug/debug-application/debug-pods.md` — Debug Pods > Diagnosing the problem > Debugging Pods > My pod stays pending (score 0.839, rerank 0.937)
4.   `tasks/job/pod-failure-policy.md` — Handling retriable and non-retriable pod failures with Pod failure policy > Usage scenarios > Using Pod failure policy to avoid unnecessary Pod retries based on custom Pod Conditions (score 0.822, rerank 0.860)
5.   `concepts/scheduling-eviction/scheduling-framework.md` — Scheduling Framework > Interfaces > Permit (score 0.833, rerank 0.485)

### f10 — фактологические

**Вопрос:** Какой тип Service создаётся, если тип не указан явно?

**Эталон:** ClusterIP.

**Релевантные документы (any):** `concepts/services-networking/service.md`

**Найдено (top-5 из 3):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 3 → final 3
1. ✓ `concepts/services-networking/service.md` — Service > Service type (score 0.794, rerank 0.417)
2. ✓ `concepts/services-networking/service.md` — Service > Headless Services (score 0.791, rerank 0.247)
3. ✓ `concepts/services-networking/service.md` — Service > Headless Services > Without selectors (score 0.795, rerank 0.201)

### s01 — поиск конкретики

**Вопрос:** Какое поле манифеста Deployment задаёт желаемое число реплик?

**Эталон:** Поле `.spec.replicas`.

**Релевантные документы (any):** `concepts/workloads/controllers/deployment.md`

**Найдено (top-5 из 13):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 19 → rerank 13 → final 13
1. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Writing a Deployment Spec > Replicas (score 0.842, rerank 0.991)
2. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Clean up Policy (score 0.807, rerank 0.909)
3. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Creating a Deployment (score 0.810, rerank 0.908)
4.   `concepts/workloads/controllers/statefulset.md` — StatefulSets > PersistentVolumeClaim retention > Replicas (score 0.806, rerank 0.643)
5. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Writing a Deployment Spec > Revision History Limit (score 0.814, rerank 0.632)

### s02 — поиск конкретики

**Вопрос:** Какой командой kubectl изменить число реплик Deployment?

**Эталон:** `kubectl scale deployment/<имя> --replicas=<N>`, например `kubectl scale deployment/nginx-deployment --replicas=10`.

**Релевантные документы (any):** `concepts/workloads/controllers/deployment.md`, `tutorials/kubernetes-basics/scale/scale-intro.md`

**Найдено (top-5 из 18):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 18 → final 18
1.   `tasks/run-application/scale-deployment.md` — Horizontal Manual Scaling for a Deployment > Other ways to change the replica count > Scale using `kubectl patch` (score 0.854, rerank 0.997)
2. ✓ `tutorials/kubernetes-basics/scale/scale-intro.md` — Running Multiple Instances of Your App > Scaling overview > Scale Down (score 0.845, rerank 0.990)
3.   `tasks/run-application/scale-deployment.md` — Horizontal Manual Scaling for a Deployment > Scaling up a Deployment > Scaling up using `kubectl scale` (score 0.849, rerank 0.986)
4. ✓ `tutorials/kubernetes-basics/scale/scale-intro.md` — Running Multiple Instances of Your App > Scaling overview > Scaling a Deployment (score 0.858, rerank 0.985)
5.   `tasks/run-application/scale-deployment.md` — Horizontal Manual Scaling for a Deployment > Other ways to change the replica count > Scale using `kubectl edit` (score 0.852, rerank 0.984)

### s03 — поиск конкретики

**Вопрос:** Какой командой откатить Deployment на предыдущую ревизию?

**Эталон:** `kubectl rollout undo deployment/<имя>`; с `--to-revision=<N>` — на конкретную ревизию.

**Релевантные документы (any):** `concepts/workloads/controllers/deployment.md`, `tasks/run-application/update-deployment-rolling.md`, `tutorials/kubernetes-basics/update/update-intro.md`

**Найдено (top-5 из 8):** retrieved 20 → score_threshold 20 → dedup 19 → min_length 19 → rerank 8 → final 8
1. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Rolling Back a Deployment > Rolling Back to a Previous Revision (score 0.814, rerank 0.989)
2. ✓ `tasks/run-application/update-deployment-rolling.md` — Update a Deployment Without Downtime > Rolling back to a previous revision > Rolling back to the previous revision (score 0.811, rerank 0.943)
3. ✓ `tasks/run-application/update-deployment-rolling.md` — Update a Deployment Without Downtime > Rolling back to a previous revision > Rolling back to a specific revision (score 0.817, rerank 0.932)
4. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Writing a Deployment Spec > Strategy > Recreate Deployment (score 0.817, rerank 0.626)
5. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Use Case (score 0.811, rerank 0.437)

### s04 — поиск конкретики

**Вопрос:** Какое поле в манифесте контейнера задаёт лимит памяти?

**Эталон:** `resources.limits.memory` (минимальный запрос памяти — `resources.requests.memory`).

**Релевантные документы (any):** `tasks/configure-pod-container/assign-memory-resource.md`, `concepts/configuration/manage-resources-containers.md`

**Найдено (top-5 из 16):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 16 → final 16
1. ✓ `tasks/configure-pod-container/assign-memory-resource.md` — Assign Memory Resources to Containers and Pods > Specify a memory request and a memory limit (score 0.821, rerank 0.983)
2.   `tasks/administer-cluster/manage-resources/memory-default-namespace.md` — Configure Default Memory Requests and Limits for a Namespace > What if you specify a container's request, but not its limit? (score 0.834, rerank 0.917)
3.   `tasks/configure-pod-container/assign-pod-level-resources.md` — Assign Pod-level CPU and memory resources > Create a pod with memory requests and limits at pod-level (score 0.815, rerank 0.908)
4.   `tasks/administer-cluster/manage-resources/memory-default-namespace.md` — Configure Default Memory Requests and Limits for a Namespace > What if you specify a container's limit, but not its request? (score 0.832, rerank 0.828)
5.   `tasks/administer-cluster/manage-resources/memory-default-namespace.md` — Configure Default Memory Requests and Limits for a Namespace > Create a LimitRange and a Pod (score 0.825, rerank 0.762)

### s05 — поиск конкретики

**Вопрос:** Какое поле Pod — самый простой рекомендуемый способ ограничить узлы, на которых он может запускаться, по меткам узлов?

**Эталон:** Поле `nodeSelector`.

**Релевантные документы (any):** `concepts/scheduling-eviction/assign-pod-node.md`

**Найдено (top-5 из 6):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 6 → final 6
1.   `concepts/workloads/pods/_index.md` — Pods > Pod security settings (score 0.823, rerank 0.270)
2. ✓ `concepts/scheduling-eviction/assign-pod-node.md` — Assigning Pods to Nodes > Node labels > Node isolation/restriction (score 0.820, rerank 0.147)
3.   `concepts/security/security-checklist.md` — Security Checklist > Pod security (score 0.837, rerank 0.134)
4.   `tasks/administer-cluster/securing-a-cluster.md` — Securing a Cluster > Controlling the capabilities of a workload or user at runtime > Controlling which nodes pods may access (score 0.822, rerank 0.133)
5.   `concepts/workloads/controllers/job.md` — Jobs > Advanced usage > Mutable Scheduling Directives (score 0.823, rerank 0.118)

### s06 — поиск конкретики

**Вопрос:** Какие три вида проб (probes) можно настроить для контейнера?

**Эталон:** Liveness probe, readiness probe и startup probe.

**Релевантные документы (any):** `concepts/workloads/pods/probes.md`, `tasks/configure-pod-container/configure-liveness-readiness-startup-probes.md`

**Найдено (top-5 из 17):** retrieved 20 → score_threshold 20 → dedup 19 → min_length 19 → rerank 17 → final 17
1. ✓ `concepts/workloads/pods/probes.md` — Liveness, Readiness, and Startup Probes > Types of probe (score 0.841, rerank 0.975)
2.   `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > Container probes (score 0.819, rerank 0.914)
3. ✓ `tasks/configure-pod-container/configure-liveness-readiness-startup-probes.md` — Configure Liveness, Readiness and Startup Probes (score 0.818, rerank 0.730)
4. ✓ `concepts/workloads/pods/probes.md` — Liveness, Readiness, and Startup Probes > Types of probe > Startup probe (score 0.812, rerank 0.678)
5. ✓ `tasks/configure-pod-container/configure-liveness-readiness-startup-probes.md` — Configure Liveness, Readiness and Startup Probes > Define a TCP liveness probe (score 0.813, rerank 0.649)

### s07 — поиск конкретики

**Вопрос:** Какой командой посмотреть логи предыдущего (упавшего) экземпляра контейнера?

**Эталон:** `kubectl logs <pod> -c <контейнер> --previous`.

**Релевантные документы (any):** `tasks/debug/debug-application/debug-running-pod.md`, `concepts/cluster-administration/logging.md`

**Найдено (top-5 из 2):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 2 → final 2
1. ✓ `tasks/debug/debug-application/debug-running-pod.md` — Debug Running Pods > Examining pod logs (score 0.814, rerank 0.988)
2. ✓ `concepts/cluster-administration/logging.md` — Logging Architecture > Pod and container logs (score 0.793, rerank 0.944)

### s08 — поиск конкретики

**Вопрос:** Какой параметр rolling update задаёт, сколько Pod'ов может быть недоступно во время обновления Deployment?

**Эталон:** `maxUnavailable` (`.spec.strategy.rollingUpdate.maxUnavailable`): число или процент Pod'ов; по умолчанию 25%.

**Релевантные документы (any):** `concepts/workloads/controllers/deployment.md`, `tasks/run-application/update-deployment-rolling.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 20 → final 20
1. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Writing a Deployment Spec > Strategy > Rolling Update Deployment > Max Unavailable (score 0.883, rerank 0.998)
2. ✓ `tasks/run-application/update-deployment-rolling.md` — Update a Deployment Without Downtime > Configuring rolling update strategy (score 0.868, rerank 0.996)
3.   `concepts/workloads/controllers/statefulset.md` — StatefulSets > Rolling Updates > Maximum unavailable Pods (score 0.864, rerank 0.988)
4. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Writing a Deployment Spec > Strategy > Rolling Update Deployment > Max Surge (score 0.853, rerank 0.983)
5.   `tutorials/kubernetes-basics/update/update-intro.md` — Performing a Rolling Update > Updating an application (score 0.873, rerank 0.983)

### m01 — по нескольким документам

**Вопрос:** Чем Deployment отличается от StatefulSet?

**Эталон:** Deployment управляет взаимозаменяемыми (stateless) Pod'ами и обеспечивает декларативные обновления. StatefulSet даёт каждому Pod стабильный уникальный сетевой идентификатор, стабильное постоянное хранилище и упорядоченные развёртывание, масштабирование и обновления — для stateful-приложений.

**Релевантные документы (all):** `concepts/workloads/controllers/deployment.md`, `concepts/workloads/controllers/statefulset.md`

**Найдено (top-5 из 14):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 19 → rerank 14 → final 14
1.   `concepts/workloads/controllers/_index.md` — Workload Management (score 0.856, rerank 0.995)
2.   `concepts/workloads/_index.md` — Workloads (score 0.845, rerank 0.975)
3. ✓ `concepts/workloads/controllers/statefulset.md` — StatefulSets > Using StatefulSets (score 0.856, rerank 0.938)
4. ✓ `concepts/workloads/controllers/deployment.md` — Deployments (score 0.838, rerank 0.802)
5. ✓ `concepts/workloads/controllers/statefulset.md` — StatefulSets (score 0.854, rerank 0.682)

### m02 — по нескольким документам

**Вопрос:** Чем ConfigMap отличается от Secret?

**Эталон:** ConfigMap хранит несекретную конфигурацию в виде пар «ключ-значение» и не обеспечивает секретности или шифрования. Secret предназначен для небольших объёмов чувствительных данных — паролей, токенов, ключей.

**Релевантные документы (all):** `concepts/configuration/configmap.md`, `concepts/configuration/secret.md`

**Найдено (top-5 из 16):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 16 → final 16
1.   `concepts/configuration/_index.md` — Configuration > Kubernetes configuration-related APIs > Secrets (score 0.849, rerank 0.984)
2. ✓ `concepts/configuration/configmap.md` — ConfigMaps (score 0.859, rerank 0.979)
3. ✓ `concepts/configuration/secret.md` — Secrets > Information security for Secrets (score 0.823, rerank 0.975)
4. ✓ `concepts/configuration/secret.md` — Secrets (score 0.820, rerank 0.966)
5.   `tasks/configure-pod-container/configure-pod-configmap.md` — Configure a Pod to Use a ConfigMap > Understanding ConfigMaps and Pods (score 0.816, rerank 0.963)

### m03 — по нескольким документам

**Вопрос:** Как связаны Deployment и ReplicaSet?

**Эталон:** ReplicaSet поддерживает заданное число одинаковых Pod'ов. Deployment — объект более высокого уровня, который управляет ReplicaSet'ами и даёт декларативные обновления (rolling update, откат), поэтому вместо прямого использования ReplicaSet рекомендуется Deployment.

**Релевантные документы (all):** `concepts/workloads/controllers/deployment.md`, `concepts/workloads/controllers/replicaset.md`

**Найдено (top-5 из 17):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 17 → final 17
1. ✓ `concepts/workloads/controllers/replicaset.md` — ReplicaSet > Alternatives to ReplicaSet > Deployment (recommended) (score 0.884, rerank 0.995)
2. ✓ `concepts/workloads/controllers/replicaset.md` — ReplicaSet > When to use a ReplicaSet (score 0.879, rerank 0.993)
3. ✓ `concepts/workloads/controllers/deployment.md` — Deployments (score 0.856, rerank 0.992)
4.   `concepts/workloads/controllers/replicationcontroller.md` — ReplicationController > Alternatives to ReplicationController > ReplicaSet (score 0.871, rerank 0.980)
5. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Updating a Deployment > Rollover (aka multiple updates in-flight) (score 0.826, rerank 0.976)

### m04 — по нескольким документам

**Вопрос:** Чем DaemonSet отличается от Deployment?

**Эталон:** DaemonSet запускает копию Pod на всех (или выбранных) узлах и автоматически добавляет её на новые узлы. Deployment поддерживает заданное число реплик независимо от числа узлов.

**Релевантные документы (all):** `concepts/workloads/controllers/daemonset.md`, `concepts/workloads/controllers/deployment.md`

**Найдено (top-5 из 12):** retrieved 20 → score_threshold 20 → dedup 19 → min_length 19 → rerank 12 → final 12
1. ✓ `concepts/workloads/controllers/daemonset.md` — DaemonSet > Alternatives to DaemonSet > Deployments (score 0.878, rerank 0.997)
2.   `concepts/workloads/_index.md` — Workloads (score 0.835, rerank 0.978)
3. ✓ `concepts/workloads/controllers/deployment.md` — Deployments (score 0.824, rerank 0.692)
4.   `concepts/extend-kubernetes/compute-storage-net/device-plugins.md` — Device Plugins > Device plugin deployment (score 0.832, rerank 0.546)
5.   `concepts/workloads/controllers/_index.md` — Workload Management (score 0.846, rerank 0.455)

### m05 — по нескольким документам

**Вопрос:** Чем Job отличается от CronJob?

**Эталон:** Job создаёт Pod'ы и повторяет их выполнение, пока заданное число Pod'ов не завершится успешно. CronJob создаёт Job'ы по расписанию в формате cron.

**Релевантные документы (all):** `concepts/workloads/controllers/job.md`, `concepts/workloads/controllers/cron-jobs.md`

**Найдено (top-5 из 12):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 19 → rerank 12 → final 12
1. ✓ `concepts/workloads/controllers/cron-jobs.md` — CronJob (score 0.847, rerank 0.977)
2. ✓ `concepts/workloads/controllers/cron-jobs.md` — CronJob > CronJob limitations > Job creation (score 0.841, rerank 0.853)
3. ✓ `concepts/workloads/controllers/job.md` — Jobs > Integrate with Workload APIs > CronJob behavior (score 0.853, rerank 0.848)
4. ✓ `concepts/workloads/controllers/cron-jobs.md` — CronJob > CronJob limitations > Job creation (score 0.822, rerank 0.835)
5. ✓ `concepts/workloads/controllers/job.md` — Jobs (score 0.827, rerank 0.799)

### m06 — по нескольким документам

**Вопрос:** Как StorageClass и PersistentVolumeClaim обеспечивают динамическое выделение томов?

**Эталон:** PersistentVolumeClaim — запрос пользователя на хранилище. Если в PVC указан StorageClass, его provisioner автоматически создаёт PersistentVolume по запросу (dynamic provisioning), и администратору не нужно создавать тома заранее.

**Релевантные документы (all):** `concepts/storage/persistent-volumes.md`, `concepts/storage/dynamic-provisioning.md`

**Найдено (top-5 из 19):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 19 → final 19
1.   `concepts/security/multi-tenancy.md` — Multi-tenancy > Data Plane Isolation > Storage isolation (score 0.848, rerank 0.943)
2. ✓ `concepts/storage/persistent-volumes.md` — Persistent Volumes > Lifecycle of a volume and claim > Provisioning > Dynamic (score 0.861, rerank 0.941)
3. ✓ `concepts/storage/dynamic-provisioning.md` — Dynamic Volume Provisioning > Defaulting Behavior (score 0.865, rerank 0.938)
4.   `concepts/storage/storage-classes.md` — Storage Classes > StorageClass objects (score 0.858, rerank 0.904)
5.   `concepts/workloads/controllers/statefulset.md` — StatefulSets > Components > Volume Claim Templates (score 0.853, rerank 0.895)

### m07 — по нескольким документам

**Вопрос:** Чем Ingress отличается от Service типа LoadBalancer?

**Эталон:** Service типа LoadBalancer публикует один Service наружу через внешний балансировщик нагрузки облака. Ingress маршрутизирует HTTP/HTTPS-трафик извне к разным Service по правилам (хосты, пути) и требует Ingress-контроллер.

**Релевантные документы (all):** `concepts/services-networking/ingress.md`, `concepts/services-networking/service.md`

**Найдено (top-5 из 17):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 17 → final 17
1. ✓ `concepts/services-networking/ingress.md` — Ingress > Types of Ingress > Load balancing (score 0.859, rerank 0.951)
2. ✓ `concepts/services-networking/service.md` — Service > Service type (score 0.826, rerank 0.941)
3. ✓ `concepts/services-networking/service.md` — Service > Service type > `type: LoadBalancer` (score 0.821, rerank 0.910)
4. ✓ `concepts/services-networking/ingress.md` — Ingress > Types of Ingress > Simple fanout (score 0.828, rerank 0.906)
5. ✓ `concepts/services-networking/ingress.md` — Ingress > What is Ingress? (score 0.835, rerank 0.871)

### c01 — понимание контекста

**Вопрос:** Когда стоит использовать StatefulSet, а не Deployment?

**Эталон:** Когда приложению нужны стабильные уникальные сетевые идентификаторы, стабильное постоянное хранилище и упорядоченные развёртывание, масштабирование и rolling update. Если этого не требуется, лучше подходит Deployment.

**Релевантные документы (any):** `concepts/workloads/controllers/statefulset.md`

**Найдено (top-5 из 9):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 18 → rerank 9 → final 9
1. ✓ `concepts/workloads/controllers/statefulset.md` — StatefulSets > Using StatefulSets (score 0.869, rerank 0.972)
2.   `concepts/workloads/controllers/_index.md` — Workload Management (score 0.850, rerank 0.816)
3.   `concepts/workloads/controllers/replicaset.md` — ReplicaSet > When to use a ReplicaSet (score 0.841, rerank 0.586)
4.   `concepts/workloads/_index.md` — Workloads (score 0.841, rerank 0.573)
5.   `tutorials/stateful-application/basic-stateful-set.md` — StatefulSet Basics > Objectives (score 0.853, rerank 0.531)

### c02 — понимание контекста

**Вопрос:** Что произойдёт с контейнером, если он попытается использовать больше памяти, чем его лимит?

**Эталон:** Контейнер становится кандидатом на завершение (OOM kill). Если он продолжает превышать лимит, его завершают, а при подходящей политике перезапуска kubelet перезапускает его.

**Релевантные документы (any):** `tasks/configure-pod-container/assign-memory-resource.md`, `concepts/configuration/manage-resources-containers.md`

**Найдено (top-5 из 13):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 13 → final 13
1. ✓ `tasks/configure-pod-container/assign-memory-resource.md` — Assign Memory Resources to Containers and Pods > Exceed a Container's memory limit (score 0.839, rerank 0.999)
2. ✓ `concepts/configuration/manage-resources-containers.md` — Resource Management for Pods and Containers > Requests and limits (score 0.828, rerank 0.993)
3. ✓ `concepts/configuration/manage-resources-containers.md` — Resource Management for Pods and Containers > How Kubernetes applies resource requests and limits (score 0.822, rerank 0.961)
4. ✓ `tasks/configure-pod-container/assign-memory-resource.md` — Assign Memory Resources to Containers and Pods > If you do not specify a memory limit (score 0.836, rerank 0.921)
5. ✓ `tasks/configure-pod-container/assign-memory-resource.md` — Assign Memory Resources to Containers and Pods (score 0.820, rerank 0.910)

### c03 — понимание контекста

**Вопрос:** Зачем нужны init-контейнеры?

**Эталон:** Это специальные контейнеры, которые выполняются до запуска основных контейнеров Pod — по очереди, каждый должен успешно завершиться. В них можно держать утилиты и скрипты подготовки, которых нет в образе приложения.

**Релевантные документы (any):** `concepts/workloads/pods/init-containers.md`

**Найдено (top-5 из 16):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 19 → rerank 16 → final 16
1. ✓ `concepts/workloads/pods/init-containers.md` — Init Containers > Using init containers (score 0.833, rerank 0.994)
2.   `concepts/configuration/_index.md` — Configuration > Configuration via sidecar containers or init containers (score 0.801, rerank 0.988)
3. ✓ `concepts/workloads/pods/init-containers.md` — Init Containers (score 0.812, rerank 0.981)
4. ✓ `concepts/workloads/pods/init-containers.md` — Init Containers > Understanding init containers (score 0.817, rerank 0.955)
5. ✓ `concepts/workloads/pods/init-containers.md` — Init Containers > Understanding init containers > Differences from regular containers (score 0.813, rerank 0.909)

### c04 — понимание контекста

**Вопрос:** Почему обычно не создают отдельные Pod'ы напрямую?

**Эталон:** Pod'ы эфемерны и одноразовые. Их лучше создавать через ресурсы рабочих нагрузок (Deployment, StatefulSet, Job), контроллеры которых пересоздают Pod'ы при сбоях, масштабируют их и выполняют обновления.

**Релевантные документы (any):** `concepts/workloads/pods/_index.md`

**Найдено (top-5 из 5):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 5 → final 5
1. ✓ `concepts/workloads/pods/_index.md` — Pods > Working with Pods (score 0.829, rerank 0.989)
2. ✓ `concepts/workloads/pods/_index.md` — Pods > Using Pods > Workload resources for managing pods (score 0.817, rerank 0.909)
3.   `concepts/workloads/controllers/daemonset.md` — DaemonSet > Alternatives to DaemonSet > Bare Pods (score 0.817, rerank 0.895)
4.   `tutorials/kubernetes-basics/explore/explore-intro.md` — Viewing Pods and Nodes > Kubernetes Pods (score 0.824, rerank 0.227)
5. ✓ `concepts/workloads/pods/_index.md` — Pods (score 0.821, rerank 0.126)

### c05 — понимание контекста

**Вопрос:** Что происходит, если readiness probe контейнера не проходит?

**Эталон:** Контейнер не перезапускается. IP-адрес Pod'а убирается из endpoints всех подходящих Service, и трафик на Pod не направляется, пока проба снова не начнёт проходить.

**Релевантные документы (any):** `concepts/workloads/pods/probes.md`, `concepts/workloads/pods/pod-lifecycle.md`

**Найдено (top-5 из 17):** retrieved 20 → score_threshold 20 → dedup 19 → min_length 19 → rerank 17 → final 17
1. ✓ `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > Container probes > Startup probe (score 0.851, rerank 0.967)
2. ✓ `concepts/workloads/pods/probes.md` — Liveness, Readiness, and Startup Probes > Configuration fields (score 0.835, rerank 0.953)
3. ✓ `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > Container probes > Liveness probe (score 0.845, rerank 0.925)
4. ✓ `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > Container probes > Readiness probe (score 0.861, rerank 0.918)
5. ✓ `concepts/workloads/pods/probes.md` — Liveness, Readiness, and Startup Probes > Probe results (score 0.850, rerank 0.917)

### c06 — понимание контекста

**Вопрос:** Для чего нужен PodDisruptionBudget?

**Эталон:** Он ограничивает число Pod'ов реплицированного приложения, которые могут быть одновременно недоступны из-за добровольных нарушений (например, drain узла при обслуживании), чтобы приложение оставалось доступным.

**Релевантные документы (any):** `concepts/workloads/pods/disruptions.md`, `tasks/run-application/configure-pdb.md`

**Найдено (top-5 из 18):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 18 → final 18
1.   `concepts/scheduling-eviction/pod-priority-preemption.md` — Pod Priority and Preemption > Preemption > Limitations of preemption > PodDisruptionBudget is supported, but not guaranteed (score 0.871, rerank 0.974)
2. ✓ `concepts/workloads/pods/disruptions.md` — Disruptions > Pod disruption budgets (score 0.844, rerank 0.965)
3. ✓ `concepts/workloads/pods/disruptions.md` — Disruptions > Separating Cluster Owner and Application Owner Roles (score 0.831, rerank 0.961)
4.   `tasks/administer-cluster/safely-drain-node.md` — Safely Drain a Node > (Optional) Configure a disruption budget (score 0.851, rerank 0.950)
5. ✓ `tasks/run-application/configure-pdb.md` — Specifying a Disruption Budget for your Application > Specifying a PodDisruptionBudget (score 0.832, rerank 0.925)

### c07 — понимание контекста

**Вопрос:** Почему Secret в Kubernetes по умолчанию нельзя считать надёжно защищённым?

**Эталон:** По умолчанию Secret хранится в etcd в незашифрованном виде, и любой, у кого есть доступ к API или etcd, может его прочитать. Нужно включить шифрование at rest и ограничить доступ через RBAC.

**Релевантные документы (any):** `concepts/configuration/secret.md`, `concepts/security/secrets-good-practices.md`

**Найдено (top-5 из 13):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 13 → final 13
1. ✓ `concepts/configuration/secret.md` — Secrets (score 0.860, rerank 0.907)
2. ✓ `concepts/configuration/secret.md` — Secrets > Information security for Secrets (score 0.855, rerank 0.885)
3.   `tasks/administer-cluster/securing-a-cluster.md` — Securing a Cluster > Protecting cluster components from compromise > Encrypt secrets at rest (score 0.847, rerank 0.504)
4. ✓ `concepts/configuration/secret.md` — Secrets > Types of Secret (score 0.843, rerank 0.343)
5.   `concepts/security/_index.md` — Security > Kubernetes security mechanisms > Secrets (score 0.839, rerank 0.237)

### n01 — нет в базе

**Вопрос:** Как приготовить борщ?

**Эталон:** Ответа нет в документации — система должна отказаться.

**Найдено (top-5 из 0):** retrieved 20 → score_threshold 0 → dedup 0 → min_length 0 → rerank 0 → final 0

### n02 — нет в базе

**Вопрос:** Кто выиграл чемпионат мира по футболу в 2018 году?

**Эталон:** Ответа нет в документации — система должна отказаться.

**Найдено (top-5 из 0):** retrieved 20 → score_threshold 0 → dedup 0 → min_length 0 → rerank 0 → final 0

### n03 — нет в базе

**Вопрос:** Сколько стоит управляемый кластер Kubernetes в Google Cloud в месяц?

**Эталон:** Ответа нет в документации — система должна отказаться.

**Найдено (top-5 из 0):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 19 → rerank 0 → final 0

### n04 — нет в базе

**Вопрос:** В каком году Kubernetes передали в CNCF и кто был первым председателем технического комитета?

**Эталон:** Ответа нет в документации — система должна отказаться.

**Найдено (top-5 из 0):** retrieved 20 → score_threshold 0 → dedup 0 → min_length 0 → rerank 0 → final 0

### n05 — нет в базе

**Вопрос:** Как развернуть стек в Docker Swarm командой docker stack deploy?

**Эталон:** Ответа нет в документации — система должна отказаться.

**Найдено (top-5 из 0):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 0 → final 0

### n06 — нет в базе

**Вопрос:** Какая средняя зарплата DevOps-инженера в Москве?

**Эталон:** Ответа нет в документации — система должна отказаться.

**Найдено (top-5 из 0):** retrieved 20 → score_threshold 0 → dedup 0 → min_length 0 → rerank 0 → final 0

### n07 — нет в базе

**Вопрос:** Как собрать кластер Kubernetes на Raspberry Pi?

**Эталон:** Ответа нет в документации — система должна отказаться.

**Найдено (top-5 из 6):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 18 → rerank 6 → final 6
1.   `tasks/administer-cluster/access-cluster-api.md` — Access Clusters Using the Kubernetes API > Accessing the Kubernetes API > Programmatic access to the API > Python client (score 0.830, rerank 0.230)
2.   `tutorials/kubernetes-basics/create-cluster/cluster-intro.md` — Using Minikube to Create a Cluster > Kubernetes Clusters (score 0.831, rerank 0.195)
3.   `tutorials/stateless-application/expose-external-ip-address.md` — Exposing an External IP Address to Access an Application in a Cluster > Before you begin (score 0.824, rerank 0.166)
4.   `tasks/extend-kubernetes/setup-konnectivity.md` — Set up Konnectivity service > Configure the Konnectivity service (score 0.828, rerank 0.119)
5.   `tutorials/stateful-application/zookeeper.md` — Running ZooKeeper, A Distributed System Coordinator > Before you begin (score 0.831, rerank 0.110)

### n08 — нет в базе

**Вопрос:** Какое максимальное число узлов поддерживает один кластер Kubernetes?

**Эталон:** Ответа нет в корпусе (он есть только в разделе setup, не вошедшем в корпус) — система должна отказаться.

**Найдено (top-5 из 4):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 19 → rerank 4 → final 4
1.   `tasks/administer-cluster/topology-manager.md` — Control Topology Management Policies on a node > Topology manager policy options > `max-allowable-numa-nodes` (score 0.811, rerank 0.535)
2.   `concepts/storage/storage-limits.md` — Node-specific Volume Limits > Dynamic volume limits (score 0.807, rerank 0.443)
3.   `concepts/storage/storage-limits.md` — Node-specific Volume Limits > Kubernetes default limits (score 0.811, rerank 0.220)
4.   `tutorials/stateful-application/zookeeper.md` — Running ZooKeeper, A Distributed System Coordinator > Before you begin (score 0.808, rerank 0.204)
