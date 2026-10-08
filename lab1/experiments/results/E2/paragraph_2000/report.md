# Прогон `E2/paragraph_2000`

## Параметры

- `collection`: k8s__multilingual-e5-base__paragraph-2000-0-h
- `embedding_model`: multilingual-e5-base
- `chunking.strategy`: paragraph
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
| 1 | 0.781 | 0.688 | 0.781 |
| 3 | 0.938 | 0.906 | 0.635 |
| 5 | 0.938 | 0.906 | 0.550 |
| 10 | 0.938 | 0.938 | 0.511 |
| 20 | 0.938 | 0.938 | 0.483 |

MRR: **0.849**

| Тип | Hit@5 | Recall@5 | MRR |
|---|--:|--:|--:|
| фактологические | 0.900 | 0.900 | 0.800 |
| поиск конкретики | 0.875 | 0.875 | 0.729 |
| по нескольким документам | 1.000 | 0.857 | 0.905 |
| понимание контекста | 1.000 | 1.000 | 1.000 |

Вопросы без ответа: контекст отсечён фильтрами в 75% случаев.
Вопросы с ответом: контекст отсечён целиком в 0% случаев.

Средняя задержка: retrieval 0.3657 с

## По вопросам

| id | Тип | Hit@5 | RR | Отказ | Correctness | Faithfulness |
|---|---|--:|--:|:-:|:-:|:-:|
| f01 | фактологические | 1.000 | 1.000 | — | — | — |
| f02 | фактологические | 0.000 | 0.000 | — | — | — |
| f03 | фактологические | 1.000 | 1.000 | — | — | — |
| f04 | фактологические | 1.000 | 1.000 | — | — | — |
| f05 | фактологические | 1.000 | 0.500 | — | — | — |
| f06 | фактологические | 1.000 | 1.000 | — | — | — |
| f07 | фактологические | 1.000 | 1.000 | — | — | — |
| f08 | фактологические | 1.000 | 1.000 | — | — | — |
| f09 | фактологические | 1.000 | 1.000 | — | — | — |
| f10 | фактологические | 1.000 | 0.500 | — | — | — |
| s01 | поиск конкретики | 1.000 | 1.000 | — | — | — |
| s02 | поиск конкретики | 1.000 | 0.500 | — | — | — |
| s03 | поиск конкретики | 1.000 | 1.000 | — | — | — |
| s04 | поиск конкретики | 1.000 | 1.000 | — | — | — |
| s05 | поиск конкретики | 0.000 | 0.000 | — | — | — |
| s06 | поиск конкретики | 1.000 | 1.000 | — | — | — |
| s07 | поиск конкретики | 1.000 | 0.333 | — | — | — |
| s08 | поиск конкретики | 1.000 | 1.000 | — | — | — |
| m01 | по нескольким документам | 1.000 | 0.333 | — | — | — |
| m02 | по нескольким документам | 1.000 | 1.000 | — | — | — |
| m03 | по нескольким документам | 1.000 | 1.000 | — | — | — |
| m04 | по нескольким документам | 1.000 | 1.000 | — | — | — |
| m05 | по нескольким документам | 1.000 | 1.000 | — | — | — |
| m06 | по нескольким документам | 1.000 | 1.000 | — | — | — |
| m07 | по нескольким документам | 1.000 | 1.000 | — | — | — |
| c01 | понимание контекста | 1.000 | 1.000 | — | — | — |
| c02 | понимание контекста | 1.000 | 1.000 | — | — | — |
| c03 | понимание контекста | 1.000 | 1.000 | — | — | — |
| c04 | понимание контекста | 1.000 | 1.000 | — | — | — |
| c05 | понимание контекста | 1.000 | 1.000 | — | — | — |
| c06 | понимание контекста | 1.000 | 1.000 | — | — | — |
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
1. ✓ `concepts/workloads/pods/_index.md` — Pods (score 0.822, rerank 0.998)
2.   `tutorials/kubernetes-basics/explore/explore-intro.md` — Viewing Pods and Nodes > Objectives (score 0.821, rerank 0.985)
3. ✓ `concepts/workloads/pods/_index.md` — Pods > Working with Pods (score 0.790, rerank 0.916)
4. ✓ `concepts/workloads/pods/_index.md` — Pods > Pods with multiple containers (score 0.788, rerank 0.897)
5.   `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle (score 0.796, rerank 0.896)

### f02 — фактологические

**Вопрос:** Какой компонент control plane хранит все данные кластера?

**Эталон:** etcd — согласованное высокодоступное хранилище «ключ-значение» для всех данных API-сервера.

**Релевантные документы (any):** `concepts/overview/components.md`

**Найдено (top-5 из 13):** retrieved 20 → score_threshold 17 → dedup 17 → min_length 17 → rerank 13 → final 13
1.   `concepts/security/multi-tenancy.md` — Multi-tenancy > Implementations > Virtual control plane per tenant (score 0.801, rerank 0.895)
2.   `concepts/architecture/_index.md` — Cluster Architecture (score 0.800, rerank 0.859)
3.   `concepts/architecture/_index.md` — Cluster Architecture > Node components > Container runtime (score 0.793, rerank 0.857)
4.   `tutorials/kubernetes-basics/create-cluster/cluster-intro.md` — Using Minikube to Create a Cluster > Kubernetes Clusters (score 0.797, rerank 0.831)
5.   `concepts/cluster-administration/observability.md` — Observability (score 0.790, rerank 0.693)

### f03 — фактологические

**Вопрос:** Какой порт обычно использует HTTP API kubelet на рабочих узлах?

**Эталон:** TCP-порт 10250.

**Релевантные документы (any):** `concepts/security/api-server-bypass-risks.md`

**Найдено (top-5 из 10):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 10 → final 10
1. ✓ `concepts/security/api-server-bypass-risks.md` — Kubernetes API Server Bypass Risks > Static Pods > Mitigations (score 0.839, rerank 0.992)
2.   `tutorials/cluster-management/kubelet-standalone.md` — Running Kubelet in Standalone Mode > Download, install, and configure the components > Download and set up the kubelet (score 0.824, rerank 0.945)
3. ✓ `concepts/security/api-server-bypass-risks.md` — Kubernetes API Server Bypass Risks > The kubelet API (score 0.837, rerank 0.912)
4.   `concepts/architecture/control-plane-node-communication.md` — Communication between Nodes and the Control Plane (score 0.827, rerank 0.909)
5.   `concepts/security/controlling-access.md` — Controlling Access to the Kubernetes API (score 0.826, rerank 0.717)

### f04 — фактологические

**Вопрос:** Из какого диапазона по умолчанию выделяются порты для Service типа NodePort?

**Эталон:** Из диапазона 30000–32767.

**Релевантные документы (any):** `concepts/services-networking/service.md`

**Найдено (top-5 из 12):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 12 → final 12
1. ✓ `concepts/services-networking/service.md` — Service > Service type > `type: NodePort` > Choosing your own port (score 0.840, rerank 0.987)
2. ✓ `concepts/services-networking/service.md` — Service > Service type > `type: NodePort` (score 0.835, rerank 0.981)
3.   `tasks/access-application-cluster/create-external-load-balancer.md` — Create an External Load Balancer > Preserving the client source IP (score 0.808, rerank 0.734)
4.   `tutorials/services/source-ip.md` — Using Source IP > Source IP for Services with `Type=ClusterIP` (score 0.801, rerank 0.669)
5. ✓ `concepts/services-networking/service.md` — Service > Service type > `type: NodePort` > IP address configuration for `type: NodePort` Services (score 0.816, rerank 0.612)

### f05 — фактологические

**Вопрос:** Что делает kube-scheduler?

**Эталон:** Отслеживает Pod'ы, ещё не назначенные на узел, и выбирает для каждого из них подходящий узел.

**Релевантные документы (any):** `concepts/overview/components.md`, `concepts/scheduling-eviction/kube-scheduler.md`

**Найдено (top-5 из 19):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 19 → final 19
1.   `concepts/scheduling-eviction/scheduler-perf-tuning.md` — Scheduler Performance Tuning (score 0.837, rerank 0.994)
2. ✓ `concepts/scheduling-eviction/kube-scheduler.md` — Kubernetes Scheduler (score 0.865, rerank 0.990)
3. ✓ `concepts/scheduling-eviction/kube-scheduler.md` — Kubernetes Scheduler > kube-scheduler (score 0.851, rerank 0.985)
4.   `concepts/cluster-administration/system-metrics.md` — Metrics For Kubernetes System Components > Component metrics > kube-controller-manager metrics (score 0.831, rerank 0.960)
5.   `concepts/extend-kubernetes/_index.md` — Extending Kubernetes > Infrastructure extensions > Network plugins (score 0.845, rerank 0.934)

### f06 — фактологические

**Вопрос:** Какое значение restartPolicy у Pod используется по умолчанию?

**Эталон:** Always.

**Релевантные документы (any):** `concepts/workloads/pods/pod-lifecycle.md`

**Найдено (top-5 из 16):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 16 → final 16
1. ✓ `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > How Pods handle problems with containers > Container restarts > Pod-level container restart policy > Restart behavior comparison (score 0.862, rerank 0.978)
2. ✓ `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > How Pods handle problems with containers > Container restarts > Container restarts and resilience (score 0.855, rerank 0.969)
3.   `concepts/services-networking/dns-pod-service.md` — DNS for Services and Pods > Pods > Pod's DNS Policy (score 0.837, rerank 0.933)
4. ✓ `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > How Pods handle problems with containers > Container restarts > Individual container restart policy and rules (score 0.844, rerank 0.920)
5. ✓ `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > How Pods handle problems with containers > Container restarts > Pod-level container restart policy > Sidecar containers and restart policies (score 0.859, rerank 0.918)

### f07 — фактологические

**Вопрос:** Какой максимальный объём данных можно хранить в одном ConfigMap?

**Эталон:** Не более 1 MiB.

**Релевантные документы (any):** `concepts/configuration/configmap.md`

**Найдено (top-5 из 9):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 9 → final 9
1. ✓ `concepts/configuration/configmap.md` — ConfigMaps (score 0.825, rerank 0.975)
2. ✓ `concepts/configuration/configmap.md` — ConfigMaps > ConfigMaps and Pods (score 0.798, rerank 0.542)
3.   `tasks/configure-pod-container/configure-pod-configmap.md` — Configure a Pod to Use a ConfigMap > Understanding ConfigMaps and Pods (score 0.787, rerank 0.267)
4.   `tutorials/configuration/configure-redis-using-configmap.md` — Configuring Redis using a ConfigMap > Real World Example: Configuring Redis using a ConfigMap (score 0.790, rerank 0.249)
5.   `concepts/storage/volumes.md` — Volumes > Types of volumes > configMap (score 0.797, rerank 0.184)

### f08 — фактологические

**Вопрос:** Для чего в Kubernetes нужны Namespace?

**Эталон:** Namespace — механизм изоляции групп ресурсов внутри одного кластера; имена ресурсов должны быть уникальны в пределах namespace, но не между namespace.

**Релевантные документы (any):** `concepts/overview/working-with-objects/namespaces.md`

**Найдено (top-5 из 14):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 14 → final 14
1. ✓ `concepts/overview/working-with-objects/namespaces.md` — Namespaces (score 0.867, rerank 0.992)
2.   `concepts/security/multi-tenancy.md` — Multi-tenancy > Terminology > Isolation (score 0.846, rerank 0.904)
3.   `tasks/administer-cluster/namespaces.md` — Share a Cluster with Namespaces > Subdividing your cluster using Kubernetes namespaces > Create pods in each namespace (score 0.860, rerank 0.896)
4.   `tasks/access-application-cluster/web-ui-dashboard.md` — Deploy and Access the Kubernetes Dashboard > Deploying containerized applications > Specifying application details (score 0.833, rerank 0.854)
5.   `tutorials/cluster-management/namespaces-walkthrough.md` — Namespaces Walkthrough (score 0.842, rerank 0.850)

### f09 — фактологические

**Вопрос:** Что означает фаза Pending у Pod?

**Эталон:** Pod принят кластером, но один или несколько контейнеров ещё не готовы к запуску — в том числе Pod ждёт планирования на узел или загрузки образов.

**Релевантные документы (any):** `concepts/workloads/pods/pod-lifecycle.md`

**Найдено (top-5 из 8):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 8 → final 8
1. ✓ `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > Pod phase (score 0.837, rerank 0.986)
2. ✓ `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle (score 0.822, rerank 0.951)
3. ✓ `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > Pod phase (score 0.817, rerank 0.763)
4.   `concepts/scheduling-eviction/scheduling-framework.md` — Scheduling Framework > Interfaces > Permit (score 0.822, rerank 0.466)
5.   `tasks/configure-pod-container/resize-container-resources.md` — Resize CPU and Memory Resources assigned to Containers > Pod resize status > How deferred resizes are retried and preempted (score 0.818, rerank 0.242)

### f10 — фактологические

**Вопрос:** Какой тип Service создаётся, если тип не указан явно?

**Эталон:** ClusterIP.

**Релевантные документы (any):** `concepts/services-networking/service.md`

**Найдено (top-5 из 3):** retrieved 20 → score_threshold 18 → dedup 18 → min_length 18 → rerank 3 → final 3
1.   `tutorials/kubernetes-basics/expose/expose-intro.md` — Using a Service to Expose Your App > Overview of Kubernetes Services (score 0.799, rerank 0.214)
2. ✓ `concepts/services-networking/service.md` — Service > Service type (score 0.791, rerank 0.152)
3. ✓ `concepts/services-networking/service.md` — Service > Service type > `type: ExternalName` (score 0.781, rerank 0.118)

### s01 — поиск конкретики

**Вопрос:** Какое поле манифеста Deployment задаёт желаемое число реплик?

**Эталон:** Поле `.spec.replicas`.

**Релевантные документы (any):** `concepts/workloads/controllers/deployment.md`

**Найдено (top-5 из 18):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 18 → final 18
1. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Writing a Deployment Spec > Replicas (score 0.828, rerank 0.978)
2. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Creating a Deployment (score 0.810, rerank 0.902)
3. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Creating a Deployment (score 0.807, rerank 0.871)
4.   `tasks/administer-cluster/node-overprovisioning.md` — Overprovision Node Capacity For A Cluster > Run Pods that request node capacity > Create the placeholder deployment (score 0.806, rerank 0.789)
5.   `tutorials/kubernetes-basics/scale/scale-intro.md` — Running Multiple Instances of Your App > Scaling overview > Scaling a Deployment (score 0.802, rerank 0.691)

### s02 — поиск конкретики

**Вопрос:** Какой командой kubectl изменить число реплик Deployment?

**Эталон:** `kubectl scale deployment/<имя> --replicas=<N>`, например `kubectl scale deployment/nginx-deployment --replicas=10`.

**Релевантные документы (any):** `concepts/workloads/controllers/deployment.md`, `tutorials/kubernetes-basics/scale/scale-intro.md`

**Найдено (top-5 из 19):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 19 → final 19
1.   `tasks/run-application/scale-deployment.md` — Horizontal Manual Scaling for a Deployment > Other ways to change the replica count > Scale using `kubectl edit` (score 0.852, rerank 0.991)
2. ✓ `tutorials/kubernetes-basics/scale/scale-intro.md` — Running Multiple Instances of Your App > Scaling overview > Scaling a Deployment (score 0.847, rerank 0.986)
3.   `tasks/manage-kubernetes-objects/update-api-object-kubectl-patch.md` — Update API Objects in Place Using kubectl patch > Use strategic merge patch to update a Deployment using the retainKeys strategy > Update an object's replica count using `kubectl patch` with `--subresource` (score 0.855, rerank 0.960)
4.   `tasks/administer-cluster/node-overprovisioning.md` — Overprovision Node Capacity For A Cluster > Run Pods that request node capacity > Create the placeholder deployment (score 0.849, rerank 0.957)
5. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Rolling Back a Deployment > Rolling Back to a Previous Revision (score 0.847, rerank 0.947)

### s03 — поиск конкретики

**Вопрос:** Какой командой откатить Deployment на предыдущую ревизию?

**Эталон:** `kubectl rollout undo deployment/<имя>`; с `--to-revision=<N>` — на конкретную ревизию.

**Релевантные документы (any):** `concepts/workloads/controllers/deployment.md`, `tasks/run-application/update-deployment-rolling.md`, `tutorials/kubernetes-basics/update/update-intro.md`

**Найдено (top-5 из 6):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 6 → final 6
1. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Rolling Back a Deployment > Checking Rollout History of a Deployment (score 0.812, rerank 0.954)
2. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Rolling Back a Deployment (score 0.810, rerank 0.851)
3. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Rolling Back a Deployment > Rolling Back to a Previous Revision (score 0.807, rerank 0.741)
4. ✓ `tasks/run-application/update-deployment-rolling.md` — Update a Deployment Without Downtime (score 0.811, rerank 0.365)
5. ✓ `concepts/workloads/controllers/deployment.md` — Deployments (score 0.817, rerank 0.283)

### s04 — поиск конкретики

**Вопрос:** Какое поле в манифесте контейнера задаёт лимит памяти?

**Эталон:** `resources.limits.memory` (минимальный запрос памяти — `resources.requests.memory`).

**Релевантные документы (any):** `tasks/configure-pod-container/assign-memory-resource.md`, `concepts/configuration/manage-resources-containers.md`

**Найдено (top-5 из 13):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 13 → final 13
1. ✓ `tasks/configure-pod-container/assign-memory-resource.md` — Assign Memory Resources to Containers and Pods (score 0.811, rerank 0.933)
2.   `tasks/administer-cluster/manage-resources/memory-default-namespace.md` — Configure Default Memory Requests and Limits for a Namespace > Create a LimitRange and a Pod (score 0.818, rerank 0.783)
3.   `tasks/configure-pod-container/assign-pod-level-resources.md` — Assign Pod-level CPU and memory resources > Limitations (score 0.809, rerank 0.726)
4.   `tasks/configure-pod-container/assign-pod-level-resources.md` — Assign Pod-level CPU and memory resources > Create a pod with memory requests and limits at pod-level (score 0.808, rerank 0.719)
5.   `tasks/administer-cluster/manage-resources/memory-constraint-namespace.md` — Configure Minimum and Maximum Memory Constraints for a Namespace > Create a LimitRange and a Pod (score 0.828, rerank 0.687)

### s05 — поиск конкретики

**Вопрос:** Какое поле Pod — самый простой рекомендуемый способ ограничить узлы, на которых он может запускаться, по меткам узлов?

**Эталон:** Поле `nodeSelector`.

**Релевантные документы (any):** `concepts/scheduling-eviction/assign-pod-node.md`

**Найдено (top-5 из 5):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 5 → final 5
1.   `concepts/security/pod-security-standards.md` — Pod Security Standards > Pod OS field (score 0.836, rerank 0.264)
2.   `concepts/workloads/pods/advanced-pod-config.md` — Advanced Pod Configuration > Pod and container level security context configuration > Security context options (score 0.824, rerank 0.139)
3.   `concepts/security/pod-security-standards.md` — Pod Security Standards > Profile Details > Restricted (score 0.820, rerank 0.113)
4.   `concepts/security/security-checklist.md` — Security Checklist > Pod security (score 0.829, rerank 0.101)
5.   `concepts/security/security-checklist.md` — Security Checklist > Network security (score 0.823, rerank 0.100)

### s06 — поиск конкретики

**Вопрос:** Какие три вида проб (probes) можно настроить для контейнера?

**Эталон:** Liveness probe, readiness probe и startup probe.

**Релевантные документы (any):** `concepts/workloads/pods/probes.md`, `tasks/configure-pod-container/configure-liveness-readiness-startup-probes.md`

**Найдено (top-5 из 15):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 15 → final 15
1. ✓ `concepts/workloads/pods/probes.md` — Liveness, Readiness, and Startup Probes (score 0.815, rerank 0.937)
2.   `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > Resizing Pods > Resizing by launching replacement Pods (score 0.813, rerank 0.853)
3.   `concepts/workloads/pods/sidecar-containers.md` — Sidecar Containers > What's next (score 0.803, rerank 0.545)
4. ✓ `concepts/workloads/pods/probes.md` — Liveness, Readiness, and Startup Probes > When to use each probe > When should you use a readiness probe? (score 0.807, rerank 0.513)
5. ✓ `tasks/configure-pod-container/configure-liveness-readiness-startup-probes.md` — Configure Liveness, Readiness and Startup Probes > Define readiness probes (score 0.818, rerank 0.400)

### s07 — поиск конкретики

**Вопрос:** Какой командой посмотреть логи предыдущего (упавшего) экземпляра контейнера?

**Эталон:** `kubectl logs <pod> -c <контейнер> --previous`.

**Релевантные документы (any):** `tasks/debug/debug-application/debug-running-pod.md`, `concepts/cluster-administration/logging.md`

**Найдено (top-5 из 3):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 3 → final 3
1.   `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > How Pods handle problems with containers (score 0.797, rerank 0.235)
2.   `tutorials/stateful-application/zookeeper.md` — Running ZooKeeper, A Distributed System Coordinator > Ensuring consistent configuration > Configuring logging (score 0.793, rerank 0.173)
3. ✓ `concepts/cluster-administration/logging.md` — Logging Architecture > Pod and container logs > How nodes handle container logs (score 0.790, rerank 0.126)

### s08 — поиск конкретики

**Вопрос:** Какой параметр rolling update задаёт, сколько Pod'ов может быть недоступно во время обновления Deployment?

**Эталон:** `maxUnavailable` (`.spec.strategy.rollingUpdate.maxUnavailable`): число или процент Pod'ов; по умолчанию 25%.

**Релевантные документы (any):** `concepts/workloads/controllers/deployment.md`, `tasks/run-application/update-deployment-rolling.md`

**Найдено (top-5 из 19):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 19 → final 19
1. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Writing a Deployment Spec > Strategy > Rolling Update Deployment > Max Surge (score 0.851, rerank 0.977)
2. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Writing a Deployment Spec > Strategy (score 0.857, rerank 0.969)
3.   `concepts/workloads/controllers/statefulset.md` — StatefulSets > Rolling Updates > Partitioned rolling updates (score 0.857, rerank 0.965)
4. ✓ `tasks/run-application/update-deployment-rolling.md` — Update a Deployment Without Downtime > Pausing and resuming a rollout > Pausing a rollout (score 0.842, rerank 0.952)
5.   `tutorials/kubernetes-basics/update/update-intro.md` — Performing a Rolling Update > Objectives (score 0.870, rerank 0.932)

### m01 — по нескольким документам

**Вопрос:** Чем Deployment отличается от StatefulSet?

**Эталон:** Deployment управляет взаимозаменяемыми (stateless) Pod'ами и обеспечивает декларативные обновления. StatefulSet даёт каждому Pod стабильный уникальный сетевой идентификатор, стабильное постоянное хранилище и упорядоченные развёртывание, масштабирование и обновления — для stateful-приложений.

**Релевантные документы (all):** `concepts/workloads/controllers/deployment.md`, `concepts/workloads/controllers/statefulset.md`

**Найдено (top-5 из 16):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 16 → final 16
1.   `concepts/workloads/controllers/_index.md` — Workload Management (score 0.856, rerank 0.995)
2.   `concepts/workloads/_index.md` — Workloads (score 0.845, rerank 0.971)
3. ✓ `concepts/workloads/controllers/statefulset.md` — StatefulSets (score 0.857, rerank 0.954)
4.   `concepts/workloads/management.md` — Managing Workloads > Updating your application without an outage (score 0.820, rerank 0.883)
5. ✓ `concepts/workloads/controllers/statefulset.md` — StatefulSets > Deployment and Scaling Guarantees (score 0.829, rerank 0.860)

### m02 — по нескольким документам

**Вопрос:** Чем ConfigMap отличается от Secret?

**Эталон:** ConfigMap хранит несекретную конфигурацию в виде пар «ключ-значение» и не обеспечивает секретности или шифрования. Secret предназначен для небольших объёмов чувствительных данных — паролей, токенов, ключей.

**Релевантные документы (all):** `concepts/configuration/configmap.md`, `concepts/configuration/secret.md`

**Найдено (top-5 из 16):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 16 → final 16
1. ✓ `concepts/configuration/configmap.md` — ConfigMaps (score 0.842, rerank 0.983)
2. ✓ `concepts/configuration/secret.md` — Secrets > Immutable Secrets > Marking a Secret as immutable (score 0.820, rerank 0.963)
3.   `concepts/configuration/_index.md` — Configuration (score 0.831, rerank 0.961)
4. ✓ `concepts/configuration/secret.md` — Secrets (score 0.813, rerank 0.945)
5.   `tasks/configure-pod-container/configure-pod-configmap.md` — Configure a Pod to Use a ConfigMap > Add ConfigMap data to a Volume > Mounted ConfigMaps are updated automatically (score 0.831, rerank 0.896)

### m03 — по нескольким документам

**Вопрос:** Как связаны Deployment и ReplicaSet?

**Эталон:** ReplicaSet поддерживает заданное число одинаковых Pod'ов. Deployment — объект более высокого уровня, который управляет ReplicaSet'ами и даёт декларативные обновления (rolling update, откат), поэтому вместо прямого использования ReplicaSet рекомендуется Deployment.

**Релевантные документы (all):** `concepts/workloads/controllers/deployment.md`, `concepts/workloads/controllers/replicaset.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 20 → final 20
1. ✓ `concepts/workloads/controllers/deployment.md` — Deployments (score 0.853, rerank 0.989)
2. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Updating a Deployment (score 0.822, rerank 0.946)
3. ✓ `concepts/workloads/controllers/replicaset.md` — ReplicaSet (score 0.858, rerank 0.928)
4.   `concepts/workloads/controllers/_index.md` — Workload Management (score 0.825, rerank 0.920)
5.   `concepts/workloads/controllers/replicationcontroller.md` — ReplicationController > Alternatives to ReplicationController > Deployment (Recommended) (score 0.834, rerank 0.917)

### m04 — по нескольким документам

**Вопрос:** Чем DaemonSet отличается от Deployment?

**Эталон:** DaemonSet запускает копию Pod на всех (или выбранных) узлах и автоматически добавляет её на новые узлы. Deployment поддерживает заданное число реплик независимо от числа узлов.

**Релевантные документы (all):** `concepts/workloads/controllers/daemonset.md`, `concepts/workloads/controllers/deployment.md`

**Найдено (top-5 из 11):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 11 → final 11
1. ✓ `concepts/workloads/controllers/daemonset.md` — DaemonSet > Alternatives to DaemonSet > Init scripts (score 0.843, rerank 0.984)
2.   `concepts/workloads/_index.md` — Workloads (score 0.835, rerank 0.975)
3.   `concepts/workloads/controllers/replicationcontroller.md` — ReplicationController > Alternatives to ReplicationController > Deployment (Recommended) (score 0.824, rerank 0.974)
4.   `concepts/workloads/controllers/replicaset.md` — ReplicaSet > Alternatives to ReplicaSet > Bare Pods (score 0.815, rerank 0.626)
5.   `concepts/extend-kubernetes/compute-storage-net/device-plugins.md` — Device Plugins > Device plugin implementation > Device plugin and unhealthy devices (score 0.819, rerank 0.559)

### m05 — по нескольким документам

**Вопрос:** Чем Job отличается от CronJob?

**Эталон:** Job создаёт Pod'ы и повторяет их выполнение, пока заданное число Pod'ов не завершится успешно. CronJob создаёт Job'ы по расписанию в формате cron.

**Релевантные документы (all):** `concepts/workloads/controllers/job.md`, `concepts/workloads/controllers/cron-jobs.md`

**Найдено (top-5 из 12):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 12 → final 12
1. ✓ `concepts/workloads/controllers/cron-jobs.md` — CronJob (score 0.834, rerank 0.950)
2. ✓ `concepts/workloads/controllers/cron-jobs.md` — CronJob > CronJob limitations > Job creation (score 0.842, rerank 0.901)
3. ✓ `concepts/workloads/controllers/job.md` — Jobs > Alternatives > Replication Controller (score 0.807, rerank 0.809)
4. ✓ `concepts/workloads/controllers/job.md` — Jobs > Integrate with Workload APIs > Higher-level controllers (score 0.824, rerank 0.800)
5.   `concepts/workloads/_index.md` — Workloads (score 0.809, rerank 0.737)

### m06 — по нескольким документам

**Вопрос:** Как StorageClass и PersistentVolumeClaim обеспечивают динамическое выделение томов?

**Эталон:** PersistentVolumeClaim — запрос пользователя на хранилище. Если в PVC указан StorageClass, его provisioner автоматически создаёт PersistentVolume по запросу (dynamic provisioning), и администратору не нужно создавать тома заранее.

**Релевантные документы (all):** `concepts/storage/persistent-volumes.md`, `concepts/storage/dynamic-provisioning.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 20 → final 20
1. ✓ `concepts/storage/persistent-volumes.md` — Persistent Volumes (score 0.833, rerank 0.934)
2. ✓ `concepts/storage/dynamic-provisioning.md` — Dynamic Volume Provisioning (score 0.857, rerank 0.912)
3. ✓ `concepts/storage/dynamic-provisioning.md` — Dynamic Volume Provisioning > Enabling Dynamic Provisioning (score 0.854, rerank 0.909)
4. ✓ `concepts/storage/persistent-volumes.md` — Persistent Volumes > Lifecycle of a volume and claim (score 0.847, rerank 0.908)
5.   `concepts/security/multi-tenancy.md` — Multi-tenancy > Data Plane Isolation > Storage isolation (score 0.840, rerank 0.878)

### m07 — по нескольким документам

**Вопрос:** Чем Ingress отличается от Service типа LoadBalancer?

**Эталон:** Service типа LoadBalancer публикует один Service наружу через внешний балансировщик нагрузки облака. Ingress маршрутизирует HTTP/HTTPS-трафик извне к разным Service по правилам (хосты, пути) и требует Ingress-контроллер.

**Релевантные документы (all):** `concepts/services-networking/ingress.md`, `concepts/services-networking/service.md`

**Найдено (top-5 из 18):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 18 → final 18
1. ✓ `concepts/services-networking/ingress.md` — Ingress > Types of Ingress > Ingress backed by a single Service (score 0.826, rerank 0.929)
2. ✓ `concepts/services-networking/service.md` — Service > Service type > `type: LoadBalancer` (score 0.825, rerank 0.905)
3. ✓ `concepts/services-networking/ingress.md` — Ingress > What is Ingress? (score 0.839, rerank 0.898)
4. ✓ `concepts/services-networking/ingress.md` — Ingress (score 0.828, rerank 0.873)
5.   `tutorials/stateless-application/expose-external-ip-address.md` — Exposing an External IP Address to Access an Application in a Cluster > Creating a service for an application running in five pods (score 0.827, rerank 0.850)

### c01 — понимание контекста

**Вопрос:** Когда стоит использовать StatefulSet, а не Deployment?

**Эталон:** Когда приложению нужны стабильные уникальные сетевые идентификаторы, стабильное постоянное хранилище и упорядоченные развёртывание, масштабирование и rolling update. Если этого не требуется, лучше подходит Deployment.

**Релевантные документы (any):** `concepts/workloads/controllers/statefulset.md`

**Найдено (top-5 из 11):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 11 → final 11
1. ✓ `concepts/workloads/controllers/statefulset.md` — StatefulSets (score 0.864, rerank 0.836)
2.   `concepts/workloads/controllers/_index.md` — Workload Management (score 0.850, rerank 0.816)
3.   `concepts/workloads/_index.md` — Workloads (score 0.841, rerank 0.536)
4. ✓ `concepts/workloads/controllers/statefulset.md` — StatefulSets > Deployment and Scaling Guarantees (score 0.831, rerank 0.211)
5.   `concepts/workloads/controllers/replicaset.md` — ReplicaSet (score 0.824, rerank 0.205)

### c02 — понимание контекста

**Вопрос:** Что произойдёт с контейнером, если он попытается использовать больше памяти, чем его лимит?

**Эталон:** Контейнер становится кандидатом на завершение (OOM kill). Если он продолжает превышать лимит, его завершают, а при подходящей политике перезапуска kubelet перезапускает его.

**Релевантные документы (any):** `tasks/configure-pod-container/assign-memory-resource.md`, `concepts/configuration/manage-resources-containers.md`

**Найдено (top-5 из 17):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 17 → final 17
1. ✓ `concepts/configuration/manage-resources-containers.md` — Resource Management for Pods and Containers > How Kubernetes applies resource requests and limits (score 0.824, rerank 0.984)
2. ✓ `tasks/configure-pod-container/assign-memory-resource.md` — Assign Memory Resources to Containers and Pods > Specify a memory request and a memory limit (score 0.829, rerank 0.973)
3.   `tasks/administer-cluster/nodelocaldns.md` — Using NodeLocal DNSCache in Kubernetes Clusters > Setting memory limits (score 0.808, rerank 0.953)
4. ✓ `concepts/configuration/manage-resources-containers.md` — Resource Management for Pods and Containers (score 0.825, rerank 0.896)
5. ✓ `tasks/configure-pod-container/assign-memory-resource.md` — Assign Memory Resources to Containers and Pods > Exceed a Container's memory limit (score 0.816, rerank 0.732)

### c03 — понимание контекста

**Вопрос:** Зачем нужны init-контейнеры?

**Эталон:** Это специальные контейнеры, которые выполняются до запуска основных контейнеров Pod — по очереди, каждый должен успешно завершиться. В них можно держать утилиты и скрипты подготовки, которых нет в образе приложения.

**Релевантные документы (any):** `concepts/workloads/pods/init-containers.md`

**Найдено (top-5 из 15):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 15 → final 15
1. ✓ `concepts/workloads/pods/init-containers.md` — Init Containers > Using init containers (score 0.823, rerank 0.970)
2. ✓ `concepts/workloads/pods/init-containers.md` — Init Containers (score 0.812, rerank 0.964)
3.   `concepts/configuration/_index.md` — Configuration > Configuration via sidecar containers or init containers (score 0.794, rerank 0.816)
4. ✓ `concepts/workloads/pods/init-containers.md` — Init Containers > Detailed behavior > Resource sharing within containers (score 0.810, rerank 0.768)
5. ✓ `concepts/workloads/pods/init-containers.md` — Init Containers > Using init containers > Examples > Init containers in use (score 0.791, rerank 0.734)

### c04 — понимание контекста

**Вопрос:** Почему обычно не создают отдельные Pod'ы напрямую?

**Эталон:** Pod'ы эфемерны и одноразовые. Их лучше создавать через ресурсы рабочих нагрузок (Deployment, StatefulSet, Job), контроллеры которых пересоздают Pod'ы при сбоях, масштабируют их и выполняют обновления.

**Релевантные документы (any):** `concepts/workloads/pods/_index.md`

**Найдено (top-5 из 5):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 5 → final 5
1. ✓ `concepts/workloads/pods/_index.md` — Pods > Working with Pods (score 0.817, rerank 0.966)
2. ✓ `concepts/workloads/pods/_index.md` — Pods > What is a Pod? (score 0.823, rerank 0.898)
3.   `concepts/workloads/controllers/daemonset.md` — DaemonSet > Alternatives to DaemonSet > Init scripts (score 0.817, rerank 0.770)
4.   `tasks/administer-cluster/securing-a-cluster.md` — Securing a Cluster > Controlling access to the Kubernetes API > API Authorization (score 0.816, rerank 0.341)
5. ✓ `concepts/workloads/pods/_index.md` — Pods (score 0.830, rerank 0.183)

### c05 — понимание контекста

**Вопрос:** Что происходит, если readiness probe контейнера не проходит?

**Эталон:** Контейнер не перезапускается. IP-адрес Pod'а убирается из endpoints всех подходящих Service, и трафик на Pod не направляется, пока проба снова не начнёт проходить.

**Релевантные документы (any):** `concepts/workloads/pods/probes.md`, `concepts/workloads/pods/pod-lifecycle.md`

**Найдено (top-5 из 19):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 19 → final 19
1. ✓ `concepts/workloads/pods/probes.md` — Liveness, Readiness, and Startup Probes > Configuration fields (score 0.833, rerank 0.900)
2. ✓ `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > Container probes > Liveness probe (score 0.848, rerank 0.888)
3. ✓ `concepts/workloads/pods/probes.md` — Liveness, Readiness, and Startup Probes (score 0.840, rerank 0.827)
4.   `tasks/configure-pod-container/configure-liveness-readiness-startup-probes.md` — Configure Liveness, Readiness and Startup Probes > Define a TCP liveness probe (score 0.829, rerank 0.812)
5.   `tasks/configure-pod-container/configure-liveness-readiness-startup-probes.md` — Configure Liveness, Readiness and Startup Probes > Define readiness probes (score 0.843, rerank 0.726)

### c06 — понимание контекста

**Вопрос:** Для чего нужен PodDisruptionBudget?

**Эталон:** Он ограничивает число Pod'ов реплицированного приложения, которые могут быть одновременно недоступны из-за добровольных нарушений (например, drain узла при обслуживании), чтобы приложение оставалось доступным.

**Релевантные документы (any):** `concepts/workloads/pods/disruptions.md`, `tasks/run-application/configure-pdb.md`

**Найдено (top-5 из 16):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 16 → final 16
1. ✓ `concepts/workloads/pods/disruptions.md` — Disruptions > Pod disruption budgets (score 0.845, rerank 0.952)
2. ✓ `concepts/workloads/pods/disruptions.md` — Disruptions > Pod disruption budgets (score 0.847, rerank 0.925)
3. ✓ `concepts/workloads/pods/disruptions.md` — Disruptions > Pod disruption conditions (score 0.839, rerank 0.893)
4. ✓ `tasks/run-application/configure-pdb.md` — Specifying a Disruption Budget for your Application > Specifying a PodDisruptionBudget (score 0.833, rerank 0.890)
5. ✓ `tasks/run-application/configure-pdb.md` — Specifying a Disruption Budget for your Application > Check the status of the PDB > Healthiness of a Pod (score 0.825, rerank 0.888)

### c07 — понимание контекста

**Вопрос:** Почему Secret в Kubernetes по умолчанию нельзя считать надёжно защищённым?

**Эталон:** По умолчанию Secret хранится в etcd в незашифрованном виде, и любой, у кого есть доступ к API или etcd, может его прочитать. Нужно включить шифрование at rest и ограничить доступ через RBAC.

**Релевантные документы (any):** `concepts/configuration/secret.md`, `concepts/security/secrets-good-practices.md`

**Найдено (top-5 из 15):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 15 → final 15
1. ✓ `concepts/configuration/secret.md` — Secrets (score 0.860, rerank 0.870)
2. ✓ `concepts/configuration/secret.md` — Secrets > Immutable Secrets > Marking a Secret as immutable (score 0.853, rerank 0.731)
3.   `concepts/security/_index.md` — Security (score 0.845, rerank 0.382)
4. ✓ `concepts/configuration/secret.md` — Secrets > Information security for Secrets (score 0.848, rerank 0.344)
5. ✓ `concepts/configuration/secret.md` — Secrets > Working with Secrets > Using a Secret (score 0.846, rerank 0.340)

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

**Найдено (top-5 из 0):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 0 → final 0

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

**Найдено (top-5 из 5):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 5 → final 5
1.   `tasks/administer-cluster/kubeadm/kubeadm-certs.md` — Certificate Management with kubeadm > Signing certificate signing requests (CSR) generated by kubeadm > Embedding certificates in kubeconfig files (score 0.832, rerank 0.313)
2.   `concepts/cluster-administration/_index.md` — Cluster Administration (score 0.832, rerank 0.279)
3.   `tutorials/kubernetes-basics/create-cluster/cluster-intro.md` — Using Minikube to Create a Cluster > Objectives (score 0.831, rerank 0.258)
4.   `tutorials/kubernetes-basics/create-cluster/cluster-intro.md` — Using Minikube to Create a Cluster > Kubernetes Clusters (score 0.829, rerank 0.242)
5.   `tasks/extend-kubernetes/setup-konnectivity.md` — Set up Konnectivity service > Configure the Konnectivity service (score 0.828, rerank 0.119)

### n08 — нет в базе

**Вопрос:** Какое максимальное число узлов поддерживает один кластер Kubernetes?

**Эталон:** Ответа нет в корпусе (он есть только в разделе setup, не вошедшем в корпус) — система должна отказаться.

**Найдено (top-5 из 3):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 3 → final 3
1.   `tasks/access-application-cluster/web-ui-dashboard.md` — Deploy and Access the Kubernetes Dashboard > Deploying containerized applications > Specifying application details (score 0.802, rerank 0.768)
2.   `tasks/administer-cluster/topology-manager.md` — Control Topology Management Policies on a node > Topology manager policy options > `max-allowable-numa-nodes` (score 0.811, rerank 0.381)
3.   `concepts/storage/storage-limits.md` — Node-specific Volume Limits (score 0.802, rerank 0.210)
