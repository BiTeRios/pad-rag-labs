# Прогон `E6/без_reranker`

## Параметры

- `collection`: k8s__multilingual-e5-base__heading-1000-0-h
- `embedding_model`: multilingual-e5-base
- `chunking.strategy`: heading
- `chunking.chunk_size`: 1000
- `chunking.chunk_overlap`: 0
- `chunking.include_heading`: True
- `reranker`: False
- `candidates`: 20
- `score_threshold`: 0.78
- `dedup_threshold`: 0.8
- `min_chars`: 50
- `rerank_min_score`: None
- `max_per_document`: 0
- `top_k`: 5
- `questions`: 40

## Retrieval (32 вопросов с ответом)

| K | Hit@K | Recall@K | Precision@K |
|--:|--:|--:|--:|
| 1 | 0.812 | 0.719 | 0.812 |
| 3 | 0.938 | 0.875 | 0.646 |
| 5 | 0.969 | 0.938 | 0.625 |
| 10 | 0.969 | 0.938 | 0.556 |
| 20 | 0.969 | 0.969 | 0.497 |

MRR: **0.878**

| Тип | Hit@5 | Recall@5 | MRR |
|---|--:|--:|--:|
| фактологические | 1.000 | 1.000 | 0.950 |
| поиск конкретики | 0.875 | 0.875 | 0.719 |
| по нескольким документам | 1.000 | 0.857 | 0.905 |
| понимание контекста | 1.000 | 1.000 | 0.929 |

Вопросы без ответа: контекст отсечён фильтрами в 50% случаев.
Вопросы с ответом: контекст отсечён целиком в 0% случаев.

Средняя задержка: retrieval 0.0345 с

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
| f10 | фактологические | 1.000 | 0.500 | — | — | — |
| s01 | поиск конкретики | 1.000 | 1.000 | — | — | — |
| s02 | поиск конкретики | 1.000 | 0.500 | — | — | — |
| s03 | поиск конкретики | 1.000 | 1.000 | — | — | — |
| s04 | поиск конкретики | 1.000 | 0.250 | — | — | — |
| s05 | поиск конкретики | 0.000 | 0.000 | — | — | — |
| s06 | поиск конкретики | 1.000 | 1.000 | — | — | — |
| s07 | поиск конкретики | 1.000 | 1.000 | — | — | — |
| s08 | поиск конкретики | 1.000 | 1.000 | — | — | — |
| m01 | по нескольким документам | 1.000 | 0.333 | — | — | — |
| m02 | по нескольким документам | 1.000 | 1.000 | — | — | — |
| m03 | по нескольким документам | 1.000 | 1.000 | — | — | — |
| m04 | по нескольким документам | 1.000 | 1.000 | — | — | — |
| m05 | по нескольким документам | 1.000 | 1.000 | — | — | — |
| m06 | по нескольким документам | 1.000 | 1.000 | — | — | — |
| m07 | по нескольким документам | 1.000 | 1.000 | — | — | — |
| c01 | понимание контекста | 1.000 | 0.500 | — | — | — |
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

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1. ✓ `concepts/workloads/pods/_index.md` — Pods (score 0.840)
2. ✓ `concepts/workloads/pods/_index.md` — Pods > What is a Pod? (score 0.826)
3.   `tutorials/kubernetes-basics/explore/explore-intro.md` — Viewing Pods and Nodes > Kubernetes Pods (score 0.817)
4. ✓ `concepts/workloads/pods/_index.md` — Pods > What is a Pod? (score 0.811)
5.   `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > Pod phase (score 0.808)

### f02 — фактологические

**Вопрос:** Какой компонент control plane хранит все данные кластера?

**Эталон:** etcd — согласованное высокодоступное хранилище «ключ-значение» для всех данных API-сервера.

**Релевантные документы (any):** `concepts/overview/components.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1. ✓ `concepts/overview/components.md` — Kubernetes Components > Core Components > Control Plane Components (score 0.823)
2.   `concepts/architecture/_index.md` — Cluster Architecture > Control plane components (score 0.818)
3.   `concepts/security/multi-tenancy.md` — Multi-tenancy > Implementations > Virtual control plane per tenant (score 0.812)
4.   `concepts/security/multi-tenancy.md` — Multi-tenancy > Implementations > Virtual control plane per tenant (score 0.807)
5.   `tutorials/kubernetes-basics/create-cluster/cluster-intro.md` — Using Minikube to Create a Cluster > Kubernetes Clusters > Cluster Diagram (score 0.806)

### f03 — фактологические

**Вопрос:** Какой порт обычно использует HTTP API kubelet на рабочих узлах?

**Эталон:** TCP-порт 10250.

**Релевантные документы (any):** `concepts/security/api-server-bypass-risks.md`

**Найдено (top-5 из 19):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 19 → final 19
1. ✓ `concepts/security/api-server-bypass-risks.md` — Kubernetes API Server Bypass Risks > The kubelet API (score 0.863)
2.   `concepts/architecture/control-plane-node-communication.md` — Communication between Nodes and the Control Plane > Control plane to node > API server to kubelet (score 0.852)
3.   `concepts/security/controlling-access.md` — Controlling Access to the Kubernetes API > Transport security (score 0.847)
4.   `tasks/administer-cluster/securing-a-cluster.md` — Securing a Cluster > Controlling access to the Kubelet (score 0.839)
5.   `tasks/extend-kubernetes/http-proxy-access-api.md` — Use an HTTP Proxy to Access the Kubernetes API > Using kubectl to start a proxy server (score 0.835)

### f04 — фактологические

**Вопрос:** Из какого диапазона по умолчанию выделяются порты для Service типа NodePort?

**Эталон:** Из диапазона 30000–32767.

**Релевантные документы (any):** `concepts/services-networking/service.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1. ✓ `concepts/services-networking/service.md` — Service > Service type > `type: NodePort` (score 0.854)
2. ✓ `concepts/services-networking/service.md` — Service > Service type > `type: NodePort` > Reserve Nodeport ranges to avoid collisions (score 0.847)
3. ✓ `concepts/services-networking/service.md` — Service > Service type > `type: LoadBalancer` > Disabling load balancer NodePort allocation (score 0.830)
4. ✓ `concepts/services-networking/service.md` — Service > Service type > `type: NodePort` (score 0.829)
5. ✓ `concepts/services-networking/service.md` — Service > Service type > `type: NodePort` > `type: NodePort` Services via localhost (score 0.827)

### f05 — фактологические

**Вопрос:** Что делает kube-scheduler?

**Эталон:** Отслеживает Pod'ы, ещё не назначенные на узел, и выбирает для каждого из них подходящий узел.

**Релевантные документы (any):** `concepts/overview/components.md`, `concepts/scheduling-eviction/kube-scheduler.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1. ✓ `concepts/scheduling-eviction/kube-scheduler.md` — Kubernetes Scheduler > kube-scheduler (score 0.876)
2.   `concepts/scheduling-eviction/scheduler-perf-tuning.md` — Scheduler Performance Tuning (score 0.870)
3.   `concepts/extend-kubernetes/_index.md` — Extending Kubernetes > Scheduling extensions (score 0.865)
4. ✓ `concepts/scheduling-eviction/kube-scheduler.md` — Kubernetes Scheduler > kube-scheduler (score 0.862)
5. ✓ `concepts/scheduling-eviction/kube-scheduler.md` — Kubernetes Scheduler (score 0.857)

### f06 — фактологические

**Вопрос:** Какое значение restartPolicy у Pod используется по умолчанию?

**Эталон:** Always.

**Релевантные документы (any):** `concepts/workloads/pods/pod-lifecycle.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1. ✓ `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > How Pods handle problems with containers > Container restarts > Pod-level container restart policy (score 0.869)
2. ✓ `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > How Pods handle problems with containers > Container restarts > Individual container restart policy and rules (score 0.868)
3. ✓ `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > How Pods handle problems with containers > Container restarts > Individual container restart policy and rules (score 0.867)
4. ✓ `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > How Pods handle problems with containers > Container restarts > Pod-level container restart policy > Sidecar containers and restart policies (score 0.865)
5. ✓ `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > How Pods handle problems with containers > Container restarts > Restart All Containers > How in-place Pod restarts work (score 0.863)

### f07 — фактологические

**Вопрос:** Какой максимальный объём данных можно хранить в одном ConfigMap?

**Эталон:** Не более 1 MiB.

**Релевантные документы (any):** `concepts/configuration/configmap.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1. ✓ `concepts/configuration/configmap.md` — ConfigMaps > ConfigMap object (score 0.826)
2. ✓ `concepts/configuration/configmap.md` — ConfigMaps > Motivation (score 0.826)
3.   `tasks/configure-pod-container/configure-pod-configmap.md` — Configure a Pod to Use a ConfigMap > Understanding ConfigMaps and Pods (score 0.813)
4. ✓ `concepts/configuration/configmap.md` — ConfigMaps > ConfigMaps and Pods (score 0.813)
5. ✓ `concepts/configuration/configmap.md` — ConfigMaps > ConfigMaps and Pods (score 0.813)

### f08 — фактологические

**Вопрос:** Для чего в Kubernetes нужны Namespace?

**Эталон:** Namespace — механизм изоляции групп ресурсов внутри одного кластера; имена ресурсов должны быть уникальны в пределах namespace, но не между namespace.

**Релевантные документы (any):** `concepts/overview/working-with-objects/namespaces.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1. ✓ `concepts/overview/working-with-objects/namespaces.md` — Namespaces (score 0.865)
2.   `concepts/security/multi-tenancy.md` — Multi-tenancy > Control plane isolation > Namespaces (score 0.865)
3. ✓ `concepts/overview/working-with-objects/namespaces.md` — Namespaces > When to Use Multiple Namespaces (score 0.858)
4.   `tutorials/cluster-management/namespaces-walkthrough.md` — Namespaces Walkthrough (score 0.853)
5.   `tasks/administer-cluster/namespaces.md` — Share a Cluster with Namespaces > Understanding the motivation for using namespaces (score 0.852)

### f09 — фактологические

**Вопрос:** Что означает фаза Pending у Pod?

**Эталон:** Pod принят кластером, но один или несколько контейнеров ещё не готовы к запуску — в том числе Pod ждёт планирования на узел или загрузки образов.

**Релевантные документы (any):** `concepts/workloads/pods/pod-lifecycle.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1. ✓ `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > Pod phase (score 0.851)
2. ✓ `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > Pod phase (score 0.843)
3.   `tasks/debug/debug-application/debug-pods.md` — Debug Pods > Diagnosing the problem > Debugging Pods > My pod stays pending (score 0.839)
4. ✓ `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > Pod phase (score 0.833)
5.   `concepts/scheduling-eviction/pod-priority-preemption.md` — Pod Priority and Preemption > Pod priority > Effect of Pod priority on scheduling order (score 0.830)

### f10 — фактологические

**Вопрос:** Какой тип Service создаётся, если тип не указан явно?

**Эталон:** ClusterIP.

**Релевантные документы (any):** `concepts/services-networking/service.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1.   `tutorials/kubernetes-basics/expose/expose-intro.md` — Using a Service to Expose Your App > Overview of Kubernetes Services (score 0.813)
2. ✓ `concepts/services-networking/service.md` — Service > Defining a Service > Services without selectors (score 0.807)
3. ✓ `concepts/services-networking/service.md` — Service > Service type > `type: LoadBalancer` (score 0.807)
4. ✓ `concepts/services-networking/service.md` — Service > Defining a Service > Services without selectors (score 0.806)
5. ✓ `concepts/services-networking/service.md` — Service > Service type > `type: LoadBalancer` > Specifying class of load balancer implementation (score 0.804)

### s01 — поиск конкретики

**Вопрос:** Какое поле манифеста Deployment задаёт желаемое число реплик?

**Эталон:** Поле `.spec.replicas`.

**Релевантные документы (any):** `concepts/workloads/controllers/deployment.md`

**Найдено (top-5 из 19):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 19 → final 19
1. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Writing a Deployment Spec > Replicas (score 0.842)
2. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Creating a Deployment (score 0.827)
3. ✓ `concepts/workloads/controllers/deployment.md` — Deployments (score 0.824)
4. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Updating a Deployment (score 0.820)
5. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Scaling a Deployment > Proportional scaling (score 0.820)

### s02 — поиск конкретики

**Вопрос:** Какой командой kubectl изменить число реплик Deployment?

**Эталон:** `kubectl scale deployment/<имя> --replicas=<N>`, например `kubectl scale deployment/nginx-deployment --replicas=10`.

**Релевантные документы (any):** `concepts/workloads/controllers/deployment.md`, `tutorials/kubernetes-basics/scale/scale-intro.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1.   `tasks/manage-kubernetes-objects/update-api-object-kubectl-patch.md` — Update API Objects in Place Using kubectl patch > Use strategic merge patch to update a Deployment using the retainKeys strategy > Update an object's replica count using `kubectl patch` with `--subresource` (score 0.862)
2. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Updating a Deployment (score 0.861)
3.   `tutorials/kubernetes-basics/deploy-app/deploy-intro.md` — Using kubectl to Create a Deployment > Deploying your first app on Kubernetes (score 0.859)
4. ✓ `tutorials/kubernetes-basics/scale/scale-intro.md` — Running Multiple Instances of Your App > Scaling overview > Scaling a Deployment (score 0.857)
5.   `tasks/manage-kubernetes-objects/declarative-config.md` — Declarative Management of Kubernetes Objects Using Configuration Files > How to update objects (score 0.856)

### s03 — поиск конкретики

**Вопрос:** Какой командой откатить Deployment на предыдущую ревизию?

**Эталон:** `kubectl rollout undo deployment/<имя>`; с `--to-revision=<N>` — на конкретную ревизию.

**Релевантные документы (any):** `concepts/workloads/controllers/deployment.md`, `tasks/run-application/update-deployment-rolling.md`, `tutorials/kubernetes-basics/update/update-intro.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Writing a Deployment Spec > Revision History Limit (score 0.826)
2.   `tasks/manage-kubernetes-objects/update-api-object-kubectl-patch.md` — Update API Objects in Place Using kubectl patch > Use strategic merge patch to update a Deployment using the retainKeys strategy (score 0.821)
3. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Updating a Deployment (score 0.820)
4. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Updating a Deployment (score 0.819)
5.   `tasks/manage-kubernetes-objects/update-api-object-kubectl-patch.md` — Update API Objects in Place Using kubectl patch > Use strategic merge patch to update a Deployment using the retainKeys strategy (score 0.819)

### s04 — поиск конкретики

**Вопрос:** Какое поле в манифесте контейнера задаёт лимит памяти?

**Эталон:** `resources.limits.memory` (минимальный запрос памяти — `resources.requests.memory`).

**Релевантные документы (any):** `tasks/configure-pod-container/assign-memory-resource.md`, `concepts/configuration/manage-resources-containers.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1.   `tasks/administer-cluster/manage-resources/memory-constraint-namespace.md` — Configure Minimum and Maximum Memory Constraints for a Namespace > Attempt to create a Pod that exceeds the maximum memory constraint (score 0.839)
2.   `tasks/administer-cluster/manage-resources/memory-default-namespace.md` — Configure Default Memory Requests and Limits for a Namespace > What if you specify a container's request, but not its limit? (score 0.837)
3.   `tasks/administer-cluster/manage-resources/memory-constraint-namespace.md` — Configure Minimum and Maximum Memory Constraints for a Namespace > Create a LimitRange and a Pod (score 0.835)
4. ✓ `tasks/configure-pod-container/assign-memory-resource.md` — Assign Memory Resources to Containers and Pods > Specify a memory request and a memory limit (score 0.835)
5.   `tasks/administer-cluster/manage-resources/memory-constraint-namespace.md` — Configure Minimum and Maximum Memory Constraints for a Namespace > Create a LimitRange and a Pod (score 0.834)

### s05 — поиск конкретики

**Вопрос:** Какое поле Pod — самый простой рекомендуемый способ ограничить узлы, на которых он может запускаться, по меткам узлов?

**Эталон:** Поле `nodeSelector`.

**Релевантные документы (any):** `concepts/scheduling-eviction/assign-pod-node.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1.   `concepts/security/security-checklist.md` — Security Checklist > Pod security (score 0.839)
2.   `concepts/security/pod-security-standards.md` — Pod Security Standards > Pod OS field > Restricted Pod Security Standard changes > OS-specific policy controls (score 0.836)
3.   `concepts/security/pod-security-admission.md` — Pod Security Admission > Pod Security Admission labels for namespaces (score 0.831)
4.   `concepts/security/pod-security-standards.md` — Pod Security Standards > Profile Details > Baseline (score 0.829)
5.   `concepts/scheduling-eviction/topology-spread-constraints.md` — Pod Topology Spread Constraints > `topologySpreadConstraints` field (score 0.829)

### s06 — поиск конкретики

**Вопрос:** Какие три вида проб (probes) можно настроить для контейнера?

**Эталон:** Liveness probe, readiness probe и startup probe.

**Релевантные документы (any):** `concepts/workloads/pods/probes.md`, `tasks/configure-pod-container/configure-liveness-readiness-startup-probes.md`

**Найдено (top-5 из 19):** retrieved 20 → score_threshold 20 → dedup 19 → min_length 19 → final 19
1. ✓ `concepts/workloads/pods/probes.md` — Liveness, Readiness, and Startup Probes > Types of probe (score 0.841)
2. ✓ `concepts/workloads/pods/probes.md` — Liveness, Readiness, and Startup Probes > What's next (score 0.824)
3. ✓ `tasks/configure-pod-container/configure-liveness-readiness-startup-probes.md` — Configure Liveness, Readiness and Startup Probes > What's next (score 0.821)
4.   `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > Container probes (score 0.819)
5.   `concepts/workloads/pods/_index.md` — Pods > Container probes (score 0.819)

### s07 — поиск конкретики

**Вопрос:** Какой командой посмотреть логи предыдущего (упавшего) экземпляра контейнера?

**Эталон:** `kubectl logs <pod> -c <контейнер> --previous`.

**Релевантные документы (any):** `tasks/debug/debug-application/debug-running-pod.md`, `concepts/cluster-administration/logging.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1. ✓ `tasks/debug/debug-application/debug-running-pod.md` — Debug Running Pods > Examining pod logs (score 0.814)
2.   `concepts/containers/container-lifecycle-hooks.md` — Container Lifecycle Hooks > Container hooks > Debugging Hook handlers (score 0.799)
3.   `tasks/configure-pod-container/attach-handler-lifecycle-event.md` — Attach Handlers to Container Lifecycle Events > What's next > Reference (score 0.799)
4.   `concepts/scheduling-eviction/node-pressure-eviction.md` — Node-pressure Eviction > Eviction signals and thresholds > Deprecated kubelet garbage collection features (score 0.798)
5.   `concepts/storage/persistent-volumes.md` — Persistent Volumes > Lifecycle of a volume and claim > PersistentVolume deletion protection finalizer (score 0.798)

### s08 — поиск конкретики

**Вопрос:** Какой параметр rolling update задаёт, сколько Pod'ов может быть недоступно во время обновления Deployment?

**Эталон:** `maxUnavailable` (`.spec.strategy.rollingUpdate.maxUnavailable`): число или процент Pod'ов; по умолчанию 25%.

**Релевантные документы (any):** `concepts/workloads/controllers/deployment.md`, `tasks/run-application/update-deployment-rolling.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Writing a Deployment Spec > Strategy > Rolling Update Deployment > Max Unavailable (score 0.883)
2. ✓ `tasks/run-application/update-deployment-rolling.md` — Update a Deployment Without Downtime > Configuring rolling update strategy (score 0.869)
3.   `tutorials/kubernetes-basics/update/update-intro.md` — Performing a Rolling Update > Updating an application (score 0.868)
4. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Writing a Deployment Spec > Strategy > Rolling Update Deployment > Max Surge (score 0.865)
5.   `concepts/workloads/controllers/statefulset.md` — StatefulSets > Rolling Updates > Maximum unavailable Pods (score 0.864)

### m01 — по нескольким документам

**Вопрос:** Чем Deployment отличается от StatefulSet?

**Эталон:** Deployment управляет взаимозаменяемыми (stateless) Pod'ами и обеспечивает декларативные обновления. StatefulSet даёт каждому Pod стабильный уникальный сетевой идентификатор, стабильное постоянное хранилище и упорядоченные развёртывание, масштабирование и обновления — для stateful-приложений.

**Релевантные документы (all):** `concepts/workloads/controllers/deployment.md`, `concepts/workloads/controllers/statefulset.md`

**Найдено (top-5 из 19):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 19 → final 19
1.   `concepts/workloads/controllers/_index.md` — Workload Management (score 0.876)
2.   `concepts/workloads/_index.md` — Workloads (score 0.858)
3. ✓ `concepts/workloads/controllers/statefulset.md` — StatefulSets > Using StatefulSets (score 0.856)
4. ✓ `concepts/workloads/controllers/statefulset.md` — StatefulSets (score 0.854)
5. ✓ `concepts/workloads/controllers/statefulset.md` — StatefulSets > What's next (score 0.847)

### m02 — по нескольким документам

**Вопрос:** Чем ConfigMap отличается от Secret?

**Эталон:** ConfigMap хранит несекретную конфигурацию в виде пар «ключ-значение» и не обеспечивает секретности или шифрования. Secret предназначен для небольших объёмов чувствительных данных — паролей, токенов, ключей.

**Релевантные документы (all):** `concepts/configuration/configmap.md`, `concepts/configuration/secret.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1. ✓ `concepts/configuration/configmap.md` — ConfigMaps (score 0.859)
2. ✓ `concepts/configuration/secret.md` — Secrets (score 0.856)
3.   `tasks/manage-kubernetes-objects/kustomization.md` — Declarative Management of Kubernetes Objects Using Kustomize > Overview of Kustomize > Generating Resources (score 0.851)
4.   `concepts/configuration/_index.md` — Configuration > Kubernetes configuration-related APIs > Secrets (score 0.849)
5.   `concepts/security/security-checklist.md` — Security Checklist > Secrets (score 0.844)

### m03 — по нескольким документам

**Вопрос:** Как связаны Deployment и ReplicaSet?

**Эталон:** ReplicaSet поддерживает заданное число одинаковых Pod'ов. Deployment — объект более высокого уровня, который управляет ReplicaSet'ами и даёт декларативные обновления (rolling update, откат), поэтому вместо прямого использования ReplicaSet рекомендуется Deployment.

**Релевантные документы (all):** `concepts/workloads/controllers/deployment.md`, `concepts/workloads/controllers/replicaset.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1. ✓ `concepts/workloads/controllers/replicaset.md` — ReplicaSet > Alternatives to ReplicaSet > Deployment (recommended) (score 0.884)
2. ✓ `concepts/workloads/controllers/replicaset.md` — ReplicaSet > When to use a ReplicaSet (score 0.879)
3.   `concepts/workloads/controllers/replicationcontroller.md` — ReplicationController > Alternatives to ReplicationController > ReplicaSet (score 0.871)
4. ✓ `concepts/workloads/controllers/replicaset.md` — ReplicaSet > What's next (score 0.868)
5. ✓ `concepts/workloads/controllers/deployment.md` — Deployments (score 0.856)

### m04 — по нескольким документам

**Вопрос:** Чем DaemonSet отличается от Deployment?

**Эталон:** DaemonSet запускает копию Pod на всех (или выбранных) узлах и автоматически добавляет её на новые узлы. Deployment поддерживает заданное число реплик независимо от числа узлов.

**Релевантные документы (all):** `concepts/workloads/controllers/daemonset.md`, `concepts/workloads/controllers/deployment.md`

**Найдено (top-5 из 19):** retrieved 20 → score_threshold 20 → dedup 19 → min_length 19 → final 19
1. ✓ `concepts/workloads/controllers/daemonset.md` — DaemonSet > Alternatives to DaemonSet > Deployments (score 0.878)
2.   `concepts/workloads/_index.md` — Workloads (score 0.850)
3.   `concepts/workloads/controllers/_index.md` — Workload Management (score 0.849)
4. ✓ `concepts/workloads/controllers/daemonset.md` — DaemonSet (score 0.846)
5. ✓ `concepts/workloads/controllers/daemonset.md` — DaemonSet > What's next (score 0.840)

### m05 — по нескольким документам

**Вопрос:** Чем Job отличается от CronJob?

**Эталон:** Job создаёт Pod'ы и повторяет их выполнение, пока заданное число Pod'ов не завершится успешно. CronJob создаёт Job'ы по расписанию в формате cron.

**Релевантные документы (all):** `concepts/workloads/controllers/job.md`, `concepts/workloads/controllers/cron-jobs.md`

**Найдено (top-5 из 19):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 19 → final 19
1. ✓ `concepts/workloads/controllers/cron-jobs.md` — CronJob (score 0.859)
2. ✓ `concepts/workloads/controllers/job.md` — Jobs > Integrate with Workload APIs > CronJob behavior (score 0.853)
3. ✓ `concepts/workloads/controllers/cron-jobs.md` — CronJob > What's next (score 0.844)
4. ✓ `concepts/workloads/controllers/cron-jobs.md` — CronJob > CronJob limitations > Job creation (score 0.843)
5. ✓ `concepts/workloads/controllers/cron-jobs.md` — CronJob > CronJob limitations > Modifying a CronJob (score 0.836)

### m06 — по нескольким документам

**Вопрос:** Как StorageClass и PersistentVolumeClaim обеспечивают динамическое выделение томов?

**Эталон:** PersistentVolumeClaim — запрос пользователя на хранилище. Если в PVC указан StorageClass, его provisioner автоматически создаёт PersistentVolume по запросу (dynamic provisioning), и администратору не нужно создавать тома заранее.

**Релевантные документы (all):** `concepts/storage/persistent-volumes.md`, `concepts/storage/dynamic-provisioning.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1. ✓ `concepts/storage/dynamic-provisioning.md` — Dynamic Volume Provisioning > Using Dynamic Provisioning (score 0.865)
2. ✓ `concepts/storage/dynamic-provisioning.md` — Dynamic Volume Provisioning > Defaulting Behavior (score 0.865)
3. ✓ `concepts/storage/persistent-volumes.md` — Persistent Volumes > Lifecycle of a volume and claim > Provisioning > Dynamic (score 0.861)
4. ✓ `concepts/storage/dynamic-provisioning.md` — Dynamic Volume Provisioning > Background (score 0.859)
5.   `concepts/storage/storage-classes.md` — Storage Classes > StorageClass objects (score 0.858)

### m07 — по нескольким документам

**Вопрос:** Чем Ingress отличается от Service типа LoadBalancer?

**Эталон:** Service типа LoadBalancer публикует один Service наружу через внешний балансировщик нагрузки облака. Ingress маршрутизирует HTTP/HTTPS-трафик извне к разным Service по правилам (хосты, пути) и требует Ingress-контроллер.

**Релевантные документы (all):** `concepts/services-networking/ingress.md`, `concepts/services-networking/service.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1. ✓ `concepts/services-networking/ingress.md` — Ingress > Types of Ingress > Load balancing (score 0.859)
2. ✓ `concepts/services-networking/ingress.md` — Ingress > Alternatives (score 0.858)
3.   `tasks/access-application-cluster/create-external-load-balancer.md` — Create an External Load Balancer > What's next (score 0.845)
4. ✓ `concepts/services-networking/service.md` — Service > Service type > `type: LoadBalancer` (score 0.840)
5.   `concepts/services-networking/ingress-controllers.md` — Ingress Controllers > Third party ingress controllers (score 0.836)

### c01 — понимание контекста

**Вопрос:** Когда стоит использовать StatefulSet, а не Deployment?

**Эталон:** Когда приложению нужны стабильные уникальные сетевые идентификаторы, стабильное постоянное хранилище и упорядоченные развёртывание, масштабирование и rolling update. Если этого не требуется, лучше подходит Deployment.

**Релевантные документы (any):** `concepts/workloads/controllers/statefulset.md`

**Найдено (top-5 из 18):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 18 → final 18
1.   `concepts/workloads/controllers/_index.md` — Workload Management (score 0.871)
2. ✓ `concepts/workloads/controllers/statefulset.md` — StatefulSets > Using StatefulSets (score 0.869)
3. ✓ `concepts/workloads/controllers/statefulset.md` — StatefulSets (score 0.857)
4.   `tutorials/stateful-application/basic-stateful-set.md` — StatefulSet Basics > Objectives (score 0.853)
5.   `concepts/workloads/_index.md` — Workloads (score 0.852)

### c02 — понимание контекста

**Вопрос:** Что произойдёт с контейнером, если он попытается использовать больше памяти, чем его лимит?

**Эталон:** Контейнер становится кандидатом на завершение (OOM kill). Если он продолжает превышать лимит, его завершают, а при подходящей политике перезапуска kubelet перезапускает его.

**Релевантные документы (any):** `tasks/configure-pod-container/assign-memory-resource.md`, `concepts/configuration/manage-resources-containers.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1. ✓ `tasks/configure-pod-container/assign-memory-resource.md` — Assign Memory Resources to Containers and Pods > Exceed a Container's memory limit (score 0.857)
2. ✓ `concepts/configuration/manage-resources-containers.md` — Resource Management for Pods and Containers > Requests and limits (score 0.839)
3. ✓ `tasks/configure-pod-container/assign-memory-resource.md` — Assign Memory Resources to Containers and Pods > If you do not specify a memory limit (score 0.836)
4. ✓ `concepts/configuration/manage-resources-containers.md` — Resource Management for Pods and Containers > Requests and limits (score 0.831)
5. ✓ `concepts/configuration/manage-resources-containers.md` — Resource Management for Pods and Containers > How Kubernetes applies resource requests and limits > Considerations for memory backed `emptyDir` volumes (score 0.828)

### c03 — понимание контекста

**Вопрос:** Зачем нужны init-контейнеры?

**Эталон:** Это специальные контейнеры, которые выполняются до запуска основных контейнеров Pod — по очереди, каждый должен успешно завершиться. В них можно держать утилиты и скрипты подготовки, которых нет в образе приложения.

**Релевантные документы (any):** `concepts/workloads/pods/init-containers.md`

**Найдено (top-5 из 19):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 19 → final 19
1. ✓ `concepts/workloads/pods/init-containers.md` — Init Containers > Using init containers (score 0.836)
2. ✓ `concepts/workloads/pods/init-containers.md` — Init Containers > Using init containers (score 0.833)
3. ✓ `concepts/workloads/pods/init-containers.md` — Init Containers > Understanding init containers (score 0.817)
4.   `tasks/debug/debug-application/debug-init-containers.md` — Debug Init Containers > Before you begin (score 0.813)
5. ✓ `concepts/workloads/pods/init-containers.md` — Init Containers > Understanding init containers > Differences from regular containers (score 0.813)

### c04 — понимание контекста

**Вопрос:** Почему обычно не создают отдельные Pod'ы напрямую?

**Эталон:** Pod'ы эфемерны и одноразовые. Их лучше создавать через ресурсы рабочих нагрузок (Deployment, StatefulSet, Job), контроллеры которых пересоздают Pod'ы при сбоях, масштабируют их и выполняют обновления.

**Релевантные документы (any):** `concepts/workloads/pods/_index.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1. ✓ `concepts/workloads/pods/_index.md` — Pods > Working with Pods (score 0.829)
2. ✓ `concepts/workloads/pods/_index.md` — Pods > What is a Pod? (score 0.824)
3.   `concepts/containers/images.md` — Images > Using a private registry > Use cases (score 0.823)
4. ✓ `concepts/workloads/pods/_index.md` — Pods (score 0.821)
5. ✓ `concepts/workloads/pods/_index.md` — Pods > Pods with multiple containers (score 0.821)

### c05 — понимание контекста

**Вопрос:** Что происходит, если readiness probe контейнера не проходит?

**Эталон:** Контейнер не перезапускается. IP-адрес Pod'а убирается из endpoints всех подходящих Service, и трафик на Pod не направляется, пока проба снова не начнёт проходить.

**Релевантные документы (any):** `concepts/workloads/pods/probes.md`, `concepts/workloads/pods/pod-lifecycle.md`

**Найдено (top-5 из 18):** retrieved 20 → score_threshold 20 → dedup 18 → min_length 18 → final 18
1. ✓ `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > Container probes > Readiness probe (score 0.861)
2.   `tasks/configure-pod-container/configure-liveness-readiness-startup-probes.md` — Configure Liveness, Readiness and Startup Probes > Define readiness probes (score 0.855)
3. ✓ `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > Container probes > Startup probe (score 0.851)
4. ✓ `concepts/workloads/pods/probes.md` — Liveness, Readiness, and Startup Probes > Probe results (score 0.850)
5. ✓ `concepts/workloads/pods/probes.md` — Liveness, Readiness, and Startup Probes > When to use each probe > When should you use a readiness probe? (score 0.846)

### c06 — понимание контекста

**Вопрос:** Для чего нужен PodDisruptionBudget?

**Эталон:** Он ограничивает число Pod'ов реплицированного приложения, которые могут быть одновременно недоступны из-за добровольных нарушений (например, drain узла при обслуживании), чтобы приложение оставалось доступным.

**Релевантные документы (any):** `concepts/workloads/pods/disruptions.md`, `tasks/run-application/configure-pdb.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1. ✓ `concepts/workloads/pods/disruptions.md` — Disruptions > Pod disruption budgets (score 0.876)
2.   `concepts/scheduling-eviction/pod-priority-preemption.md` — Pod Priority and Preemption > Preemption > Limitations of preemption > PodDisruptionBudget is supported, but not guaranteed (score 0.871)
3. ✓ `tasks/run-application/configure-pdb.md` — Specifying a Disruption Budget for your Application > Protecting an Application with a PodDisruptionBudget (score 0.863)
4.   `tasks/administer-cluster/safely-drain-node.md` — Safely Drain a Node > (Optional) Configure a disruption budget (score 0.851)
5. ✓ `concepts/workloads/pods/disruptions.md` — Disruptions > Pod disruption budgets (score 0.847)

### c07 — понимание контекста

**Вопрос:** Почему Secret в Kubernetes по умолчанию нельзя считать надёжно защищённым?

**Эталон:** По умолчанию Secret хранится в etcd в незашифрованном виде, и любой, у кого есть доступ к API или etcd, может его прочитать. Нужно включить шифрование at rest и ограничить доступ через RBAC.

**Релевантные документы (any):** `concepts/configuration/secret.md`, `concepts/security/secrets-good-practices.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1. ✓ `concepts/configuration/secret.md` — Secrets > Uses for Secrets > Alternatives to Secrets (score 0.859)
2. ✓ `concepts/configuration/secret.md` — Secrets (score 0.856)
3. ✓ `concepts/configuration/secret.md` — Secrets > Information security for Secrets (score 0.852)
4. ✓ `concepts/configuration/secret.md` — Secrets > Information security for Secrets (score 0.851)
5. ✓ `concepts/configuration/secret.md` — Secrets (score 0.849)

### n01 — нет в базе

**Вопрос:** Как приготовить борщ?

**Эталон:** Ответа нет в документации — система должна отказаться.

**Найдено (top-5 из 0):** retrieved 20 → score_threshold 0 → dedup 0 → min_length 0 → final 0

### n02 — нет в базе

**Вопрос:** Кто выиграл чемпионат мира по футболу в 2018 году?

**Эталон:** Ответа нет в документации — система должна отказаться.

**Найдено (top-5 из 0):** retrieved 20 → score_threshold 0 → dedup 0 → min_length 0 → final 0

### n03 — нет в базе

**Вопрос:** Сколько стоит управляемый кластер Kubernetes в Google Cloud в месяц?

**Эталон:** Ответа нет в документации — система должна отказаться.

**Найдено (top-5 из 19):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 19 → final 19
1.   `concepts/policy/resource-quotas.md` — Resource Quotas > Viewing and Setting Quotas (score 0.813)
2.   `tasks/administer-cluster/kubelet-config-file.md` — Set Kubelet Parameters Via A Configuration File > Viewing the kubelet configuration (score 0.811)
3.   `tasks/debug/debug-application/debug-running-pod.md` — Debug Running Pods > Using `kubectl describe pod` to fetch details about pods (score 0.808)
4.   `concepts/cluster-administration/system-metrics.md` — Metrics For Kubernetes System Components > Component metrics > kube-controller-manager metrics (score 0.807)
5.   `tasks/administer-cluster/kubelet-config-file.md` — Set Kubelet Parameters Via A Configuration File > Viewing the kubelet configuration (score 0.807)

### n04 — нет в базе

**Вопрос:** В каком году Kubernetes передали в CNCF и кто был первым председателем технического комитета?

**Эталон:** Ответа нет в документации — система должна отказаться.

**Найдено (top-5 из 0):** retrieved 20 → score_threshold 0 → dedup 0 → min_length 0 → final 0

### n05 — нет в базе

**Вопрос:** Как развернуть стек в Docker Swarm командой docker stack deploy?

**Эталон:** Ответа нет в документации — система должна отказаться.

**Найдено (top-5 из 19):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 19 → final 19
1.   `tasks/configure-pod-container/translate-compose-kubernetes.md` — Translate a Docker Compose File to Kubernetes Resources > `kompose convert` > OpenShift `kompose convert` example (score 0.818)
2.   `tasks/administer-cluster/migrating-from-dockershim/migrating-telemetry-and-security-agents.md` — Migrating telemetry and security agents from dockershim > Migration from dockershim > SignalFx (Splunk) (score 0.815)
3.   `tasks/administer-cluster/kubelet-config-file.md` — Set Kubelet Parameters Via A Configuration File > Viewing the kubelet configuration (score 0.813)
4.   `tasks/configure-pod-container/translate-compose-kubernetes.md` — Translate a Docker Compose File to Kubernetes Resources > Alternative Conversions (score 0.812)
5.   `concepts/containers/container-lifecycle-hooks.md` — Container Lifecycle Hooks > Container hooks > Debugging Hook handlers (score 0.810)

### n06 — нет в базе

**Вопрос:** Какая средняя зарплата DevOps-инженера в Москве?

**Эталон:** Ответа нет в документации — система должна отказаться.

**Найдено (top-5 из 0):** retrieved 20 → score_threshold 0 → dedup 0 → min_length 0 → final 0

### n07 — нет в базе

**Вопрос:** Как собрать кластер Kubernetes на Raspberry Pi?

**Эталон:** Ответа нет в документации — система должна отказаться.

**Найдено (top-5 из 17):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 17 → final 17
1.   `tasks/extend-kubernetes/configure-multiple-schedulers.md` — Configure Multiple Schedulers > Package the scheduler (score 0.834)
2.   `tasks/administer-cluster/access-cluster-api.md` — Access Clusters Using the Kubernetes API > Accessing the Kubernetes API > Programmatic access to the API > dotnet client (score 0.833)
3.   `tasks/configure-pod-container/translate-compose-kubernetes.md` — Translate a Docker Compose File to Kubernetes Resources > Restart (score 0.833)
4.   `tutorials/kubernetes-basics/create-cluster/_index.md` — Create a Cluster (score 0.832)
5.   `tutorials/stateful-application/zookeeper.md` — Running ZooKeeper, A Distributed System Coordinator > Before you begin (score 0.831)

### n08 — нет в базе

**Вопрос:** Какое максимальное число узлов поддерживает один кластер Kubernetes?

**Эталон:** Ответа нет в корпусе (он есть только в разделе setup, не вошедшем в корпус) — система должна отказаться.

**Найдено (top-5 из 19):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 19 → final 19
1.   `concepts/services-networking/endpoint-slices.md` — EndpointSlices > EndpointSlice API (score 0.815)
2.   `concepts/containers/images.md` — Images > Serial and parallel image pulls > Maximum parallel image pulls (score 0.815)
3.   `tasks/administer-cluster/kubelet-config-file.md` — Set Kubelet Parameters Via A Configuration File > Viewing the kubelet configuration (score 0.814)
4.   `concepts/workloads/pods/user-namespaces.md` — User Namespaces > ID count for each of Pods (score 0.813)
5.   `tasks/configure-pod-container/quality-service-pod.md` — Configure Quality of Service for Pods > Create a Pod that gets assigned a QoS class of BestEffort (score 0.812)
