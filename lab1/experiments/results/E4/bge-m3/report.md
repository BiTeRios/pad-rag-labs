# Прогон `E4/bge-m3`

## Параметры

- `collection`: k8s__bge-m3__heading-1000-0-h
- `embedding_model`: bge-m3
- `chunking.strategy`: heading
- `chunking.chunk_size`: 1000
- `chunking.chunk_overlap`: 0
- `chunking.include_heading`: True
- `reranker`: False
- `candidates`: 20
- `score_threshold`: 0
- `dedup_threshold`: 0.8
- `min_chars`: 50
- `rerank_min_score`: None
- `max_per_document`: 0
- `top_k`: 5
- `questions`: 40

## Retrieval (32 вопросов с ответом)

| K | Hit@K | Recall@K | Precision@K |
|--:|--:|--:|--:|
| 1 | 0.750 | 0.656 | 0.750 |
| 3 | 1.000 | 0.922 | 0.688 |
| 5 | 1.000 | 0.938 | 0.631 |
| 10 | 1.000 | 0.984 | 0.588 |
| 20 | 1.000 | 1.000 | 0.524 |

MRR: **0.859**

| Тип | Hit@5 | Recall@5 | MRR |
|---|--:|--:|--:|
| фактологические | 1.000 | 1.000 | 0.817 |
| поиск конкретики | 1.000 | 1.000 | 0.812 |
| по нескольким документам | 1.000 | 0.714 | 0.905 |
| понимание контекста | 1.000 | 1.000 | 0.929 |

Вопросы без ответа: контекст отсечён фильтрами в 0% случаев.
Вопросы с ответом: контекст отсечён целиком в 0% случаев.

Средняя задержка: retrieval 0.0505 с

## По вопросам

| id | Тип | Hit@5 | RR | Отказ | Correctness | Faithfulness |
|---|---|--:|--:|:-:|:-:|:-:|
| f01 | фактологические | 1.000 | 1.000 | — | — | — |
| f02 | фактологические | 1.000 | 0.333 | — | — | — |
| f03 | фактологические | 1.000 | 1.000 | — | — | — |
| f04 | фактологические | 1.000 | 1.000 | — | — | — |
| f05 | фактологические | 1.000 | 1.000 | — | — | — |
| f06 | фактологические | 1.000 | 1.000 | — | — | — |
| f07 | фактологические | 1.000 | 1.000 | — | — | — |
| f08 | фактологические | 1.000 | 0.500 | — | — | — |
| f09 | фактологические | 1.000 | 1.000 | — | — | — |
| f10 | фактологические | 1.000 | 0.333 | — | — | — |
| s01 | поиск конкретики | 1.000 | 1.000 | — | — | — |
| s02 | поиск конкретики | 1.000 | 0.500 | — | — | — |
| s03 | поиск конкретики | 1.000 | 1.000 | — | — | — |
| s04 | поиск конкретики | 1.000 | 0.500 | — | — | — |
| s05 | поиск конкретики | 1.000 | 0.500 | — | — | — |
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
1. ✓ `concepts/workloads/pods/_index.md` — Pods (score 0.693)
2.   `tutorials/kubernetes-basics/explore/explore-intro.md` — Viewing Pods and Nodes > Kubernetes Pods (score 0.663)
3. ✓ `concepts/workloads/pods/_index.md` — Pods > What is a Pod? (score 0.650)
4.   `tutorials/kubernetes-basics/explore/explore-intro.md` — Viewing Pods and Nodes > Kubernetes Pods (score 0.650)
5. ✓ `concepts/workloads/pods/_index.md` — Pods > Resource sharing and communication > Storage in Pods (score 0.622)

### f02 — фактологические

**Вопрос:** Какой компонент control plane хранит все данные кластера?

**Эталон:** etcd — согласованное высокодоступное хранилище «ключ-значение» для всех данных API-сервера.

**Релевантные документы (any):** `concepts/overview/components.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1.   `tutorials/kubernetes-basics/create-cluster/cluster-intro.md` — Using Minikube to Create a Cluster > Kubernetes Clusters > Cluster Diagram (score 0.637)
2.   `concepts/architecture/_index.md` — Cluster Architecture > Control plane components (score 0.633)
3. ✓ `concepts/overview/components.md` — Kubernetes Components > Core Components > Control Plane Components (score 0.606)
4.   `concepts/security/multi-tenancy.md` — Multi-tenancy > Implementations > Virtual control plane per tenant (score 0.600)
5.   `concepts/security/_index.md` — Security > Kubernetes security mechanisms > Control plane protection (score 0.599)

### f03 — фактологические

**Вопрос:** Какой порт обычно использует HTTP API kubelet на рабочих узлах?

**Эталон:** TCP-порт 10250.

**Релевантные документы (any):** `concepts/security/api-server-bypass-risks.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1. ✓ `concepts/security/api-server-bypass-risks.md` — Kubernetes API Server Bypass Risks > The kubelet API (score 0.745)
2.   `concepts/workloads/pods/probes.md` — Liveness, Readiness, and Startup Probes > Probe mechanism details > HTTP probes (score 0.680)
3.   `tutorials/cluster-management/kubelet-standalone.md` — Running Kubelet in Standalone Mode > Download, install, and configure the components > Download and set up the kubelet (score 0.661)
4.   `concepts/architecture/control-plane-node-communication.md` — Communication between Nodes and the Control Plane > Control plane to node > API server to kubelet (score 0.661)
5.   `tutorials/cluster-management/kubelet-standalone.md` — Running Kubelet in Standalone Mode > Run a Pod in the kubelet > Find out information about the kubelet and the Pod (score 0.650)

### f04 — фактологические

**Вопрос:** Из какого диапазона по умолчанию выделяются порты для Service типа NodePort?

**Эталон:** Из диапазона 30000–32767.

**Релевантные документы (any):** `concepts/services-networking/service.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1. ✓ `concepts/services-networking/service.md` — Service > Service type > `type: NodePort` (score 0.677)
2. ✓ `concepts/services-networking/service.md` — Service > Service type > `type: NodePort` > Reserve Nodeport ranges to avoid collisions (score 0.671)
3.   `tutorials/services/source-ip.md` — Using Source IP > Source IP for Services with `Type=NodePort` (score 0.628)
4. ✓ `concepts/services-networking/service.md` — Service > Service type > `type: NodePort` > IP address configuration for `type: NodePort` Services (score 0.623)
5. ✓ `concepts/services-networking/service.md` — Service > Service type > `type: NodePort` > Choosing your own port (score 0.616)

### f05 — фактологические

**Вопрос:** Что делает kube-scheduler?

**Эталон:** Отслеживает Pod'ы, ещё не назначенные на узел, и выбирает для каждого из них подходящий узел.

**Релевантные документы (any):** `concepts/overview/components.md`, `concepts/scheduling-eviction/kube-scheduler.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1. ✓ `concepts/scheduling-eviction/kube-scheduler.md` — Kubernetes Scheduler > kube-scheduler (score 0.762)
2.   `concepts/scheduling-eviction/scheduler-perf-tuning.md` — Scheduler Performance Tuning (score 0.729)
3. ✓ `concepts/scheduling-eviction/kube-scheduler.md` — Kubernetes Scheduler > kube-scheduler > Node selection in kube-scheduler (score 0.718)
4. ✓ `concepts/scheduling-eviction/kube-scheduler.md` — Kubernetes Scheduler > kube-scheduler (score 0.712)
5.   `concepts/extend-kubernetes/_index.md` — Extending Kubernetes > Scheduling extensions (score 0.708)

### f06 — фактологические

**Вопрос:** Какое значение restartPolicy у Pod используется по умолчанию?

**Эталон:** Always.

**Релевантные документы (any):** `concepts/workloads/pods/pod-lifecycle.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1. ✓ `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > How Pods handle problems with containers > Container restarts > Pod-level container restart policy (score 0.724)
2. ✓ `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > How Pods handle problems with containers > Container restarts > Restart All Containers > How in-place Pod restarts work (score 0.687)
3. ✓ `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > How Pods handle problems with containers > Container restarts > Pod-level container restart policy > Sidecar containers and restart policies (score 0.675)
4. ✓ `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > How Pods handle problems with containers > Container restarts > Individual container restart policy and rules (score 0.674)
5. ✓ `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > How Pods handle problems with containers > Container restarts > Pod-level container restart policy > Restart behavior comparison (score 0.674)

### f07 — фактологические

**Вопрос:** Какой максимальный объём данных можно хранить в одном ConfigMap?

**Эталон:** Не более 1 MiB.

**Релевантные документы (any):** `concepts/configuration/configmap.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1. ✓ `concepts/configuration/configmap.md` — ConfigMaps > Motivation (score 0.700)
2. ✓ `concepts/configuration/configmap.md` — ConfigMaps > ConfigMap object (score 0.656)
3.   `tasks/configure-pod-container/configure-pod-configmap.md` — Configure a Pod to Use a ConfigMap > Understanding ConfigMaps and Pods (score 0.641)
4. ✓ `concepts/configuration/configmap.md` — ConfigMaps > ConfigMaps and Pods (score 0.634)
5.   `concepts/storage/volumes.md` — Volumes > Types of volumes > configMap (score 0.629)

### f08 — фактологические

**Вопрос:** Для чего в Kubernetes нужны Namespace?

**Эталон:** Namespace — механизм изоляции групп ресурсов внутри одного кластера; имена ресурсов должны быть уникальны в пределах namespace, но не между namespace.

**Релевантные документы (any):** `concepts/overview/working-with-objects/namespaces.md`

**Найдено (top-5 из 19):** retrieved 20 → score_threshold 20 → dedup 19 → min_length 19 → final 19
1.   `concepts/security/multi-tenancy.md` — Multi-tenancy > Control plane isolation > Namespaces (score 0.748)
2. ✓ `concepts/overview/working-with-objects/namespaces.md` — Namespaces (score 0.744)
3. ✓ `concepts/overview/working-with-objects/namespaces.md` — Namespaces > When to Use Multiple Namespaces (score 0.732)
4.   `tasks/administer-cluster/namespaces.md` — Share a Cluster with Namespaces > Understanding the motivation for using namespaces (score 0.712)
5.   `tutorials/cluster-management/namespaces-walkthrough.md` — Namespaces Walkthrough (score 0.705)

### f09 — фактологические

**Вопрос:** Что означает фаза Pending у Pod?

**Эталон:** Pod принят кластером, но один или несколько контейнеров ещё не готовы к запуску — в том числе Pod ждёт планирования на узел или загрузки образов.

**Релевантные документы (any):** `concepts/workloads/pods/pod-lifecycle.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1. ✓ `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > Pod phase (score 0.684)
2. ✓ `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > Container states > `Waiting` (score 0.663)
3.   `tasks/configure-pod-container/assign-cpu-resource.md` — Assign CPU Resources to Containers and Pods > Specify a CPU request that is too big for your Nodes (score 0.655)
4. ✓ `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > Pod phase (score 0.655)
5. ✓ `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > Pod phase (score 0.648)

### f10 — фактологические

**Вопрос:** Какой тип Service создаётся, если тип не указан явно?

**Эталон:** ClusterIP.

**Релевантные документы (any):** `concepts/services-networking/service.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1.   `tutorials/kubernetes-basics/expose/expose-intro.md` — Using a Service to Expose Your App > Overview of Kubernetes Services (score 0.647)
2.   `tutorials/kubernetes-basics/expose/expose-intro.md` — Using a Service to Expose Your App > Overview of Kubernetes Services (score 0.630)
3. ✓ `concepts/services-networking/service.md` — Service > Service type (score 0.606)
4. ✓ `concepts/services-networking/service.md` — Service > Defining a Service (score 0.602)
5. ✓ `concepts/services-networking/service.md` — Service > Headless Services (score 0.591)

### s01 — поиск конкретики

**Вопрос:** Какое поле манифеста Deployment задаёт желаемое число реплик?

**Эталон:** Поле `.spec.replicas`.

**Релевантные документы (any):** `concepts/workloads/controllers/deployment.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Creating a Deployment (score 0.647)
2. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Writing a Deployment Spec > Replicas (score 0.629)
3. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Creating a Deployment (score 0.624)
4. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Clean up Policy (score 0.620)
5.   `tutorials/kubernetes-basics/scale/scale-intro.md` — Running Multiple Instances of Your App > Scaling overview > Scaling a Deployment (score 0.615)

### s02 — поиск конкретики

**Вопрос:** Какой командой kubectl изменить число реплик Deployment?

**Эталон:** `kubectl scale deployment/<имя> --replicas=<N>`, например `kubectl scale deployment/nginx-deployment --replicas=10`.

**Релевантные документы (any):** `concepts/workloads/controllers/deployment.md`, `tutorials/kubernetes-basics/scale/scale-intro.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1.   `tasks/run-application/scale-deployment.md` — Horizontal Manual Scaling for a Deployment > Other ways to change the replica count > Scale using `kubectl patch` (score 0.723)
2. ✓ `tutorials/kubernetes-basics/scale/scale-intro.md` — Running Multiple Instances of Your App > Scaling overview > Scaling a Deployment (score 0.694)
3.   `tasks/run-application/scale-deployment.md` — Horizontal Manual Scaling for a Deployment > Other ways to change the replica count > Scale using `kubectl edit` (score 0.680)
4.   `tasks/manage-kubernetes-objects/update-api-object-kubectl-patch.md` — Update API Objects in Place Using kubectl patch > Use strategic merge patch to update a Deployment using the retainKeys strategy > Update an object's replica count using `kubectl patch` with `--subresource` (score 0.677)
5. ✓ `tutorials/kubernetes-basics/scale/scale-intro.md` — Running Multiple Instances of Your App > Scaling overview > Scale Down (score 0.675)

### s03 — поиск конкретики

**Вопрос:** Какой командой откатить Deployment на предыдущую ревизию?

**Эталон:** `kubectl rollout undo deployment/<имя>`; с `--to-revision=<N>` — на конкретную ревизию.

**Релевантные документы (any):** `concepts/workloads/controllers/deployment.md`, `tasks/run-application/update-deployment-rolling.md`, `tutorials/kubernetes-basics/update/update-intro.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Rolling Back a Deployment > Rolling Back to a Previous Revision (score 0.677)
2. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Rolling Back a Deployment (score 0.624)
3. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Rolling Back a Deployment > Rolling Back to a Previous Revision (score 0.621)
4. ✓ `tutorials/kubernetes-basics/update/update-intro.md` — Performing a Rolling Update > Rolling updates overview > Roll back an update (score 0.621)
5. ✓ `tasks/run-application/update-deployment-rolling.md` — Update a Deployment Without Downtime > Rolling back to a previous revision > Rolling back to a specific revision (score 0.617)

### s04 — поиск конкретики

**Вопрос:** Какое поле в манифесте контейнера задаёт лимит памяти?

**Эталон:** `resources.limits.memory` (минимальный запрос памяти — `resources.requests.memory`).

**Релевантные документы (any):** `tasks/configure-pod-container/assign-memory-resource.md`, `concepts/configuration/manage-resources-containers.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1.   `tasks/administer-cluster/manage-resources/memory-default-namespace.md` — Configure Default Memory Requests and Limits for a Namespace > What if you specify a container's request, but not its limit? (score 0.677)
2. ✓ `tasks/configure-pod-container/assign-memory-resource.md` — Assign Memory Resources to Containers and Pods > Specify a memory request and a memory limit (score 0.674)
3.   `tasks/administer-cluster/manage-resources/memory-constraint-namespace.md` — Configure Minimum and Maximum Memory Constraints for a Namespace > Create a Pod that does not specify any memory request or limit (score 0.672)
4.   `tasks/administer-cluster/manage-resources/memory-constraint-namespace.md` — Configure Minimum and Maximum Memory Constraints for a Namespace > Create a LimitRange and a Pod (score 0.671)
5.   `tasks/administer-cluster/manage-resources/memory-constraint-namespace.md` — Configure Minimum and Maximum Memory Constraints for a Namespace > Attempt to create a Pod that exceeds the maximum memory constraint (score 0.670)

### s05 — поиск конкретики

**Вопрос:** Какое поле Pod — самый простой рекомендуемый способ ограничить узлы, на которых он может запускаться, по меткам узлов?

**Эталон:** Поле `nodeSelector`.

**Релевантные документы (any):** `concepts/scheduling-eviction/assign-pod-node.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1.   `tasks/manage-daemon/pods-some-nodes.md` — Running Pods on Only Some Nodes > Running Pods on only some Nodes > Step 2: Create the manifest (score 0.624)
2. ✓ `concepts/scheduling-eviction/assign-pod-node.md` — Assigning Pods to Nodes (score 0.618)
3. ✓ `concepts/scheduling-eviction/assign-pod-node.md` — Assigning Pods to Nodes > Affinity and anti-affinity > Inter-pod affinity and anti-affinity > Pod Affinity Example (score 0.607)
4.   `concepts/workloads/pods/_index.md` — Pods > Pod security settings (score 0.604)
5.   `tutorials/security/ns-level-pss.md` — Apply Pod Security Standards at the Namespace Level > Verify the Pod Security Standard enforcement (score 0.600)

### s06 — поиск конкретики

**Вопрос:** Какие три вида проб (probes) можно настроить для контейнера?

**Эталон:** Liveness probe, readiness probe и startup probe.

**Релевантные документы (any):** `concepts/workloads/pods/probes.md`, `tasks/configure-pod-container/configure-liveness-readiness-startup-probes.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1. ✓ `concepts/workloads/pods/probes.md` — Liveness, Readiness, and Startup Probes > Types of probe (score 0.642)
2. ✓ `tasks/configure-pod-container/configure-liveness-readiness-startup-probes.md` — Configure Liveness, Readiness and Startup Probes > Define a TCP liveness probe (score 0.582)
3.   `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > Container probes (score 0.569)
4. ✓ `concepts/workloads/pods/probes.md` — Liveness, Readiness, and Startup Probes > Check mechanisms (score 0.569)
5. ✓ `tasks/configure-pod-container/configure-liveness-readiness-startup-probes.md` — Configure Liveness, Readiness and Startup Probes (score 0.564)

### s07 — поиск конкретики

**Вопрос:** Какой командой посмотреть логи предыдущего (упавшего) экземпляра контейнера?

**Эталон:** `kubectl logs <pod> -c <контейнер> --previous`.

**Релевантные документы (any):** `tasks/debug/debug-application/debug-running-pod.md`, `concepts/cluster-administration/logging.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1. ✓ `tasks/debug/debug-application/debug-running-pod.md` — Debug Running Pods > Examining pod logs (score 0.643)
2. ✓ `concepts/cluster-administration/logging.md` — Logging Architecture > Pod and container logs (score 0.611)
3.   `tasks/manage-daemon/create-daemon-set.md` — Building a Basic DaemonSet > Define the DaemonSet (score 0.585)
4. ✓ `tasks/debug/debug-application/debug-running-pod.md` — Debug Running Pods > Debugging with container exec (score 0.583)
5.   `tasks/debug/debug-cluster/crictl.md` — Debugging Kubernetes nodes with crictl > Example crictl commands > Get a container's logs (score 0.581)

### s08 — поиск конкретики

**Вопрос:** Какой параметр rolling update задаёт, сколько Pod'ов может быть недоступно во время обновления Deployment?

**Эталон:** `maxUnavailable` (`.spec.strategy.rollingUpdate.maxUnavailable`): число или процент Pod'ов; по умолчанию 25%.

**Релевантные документы (any):** `concepts/workloads/controllers/deployment.md`, `tasks/run-application/update-deployment-rolling.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Writing a Deployment Spec > Strategy > Rolling Update Deployment > Max Unavailable (score 0.742)
2. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Writing a Deployment Spec > Strategy > Rolling Update Deployment (score 0.706)
3. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Writing a Deployment Spec > Strategy > Rolling Update Deployment > Max Surge (score 0.698)
4.   `tutorials/kubernetes-basics/update/update-intro.md` — Performing a Rolling Update > Updating an application (score 0.694)
5. ✓ `tasks/run-application/update-deployment-rolling.md` — Update a Deployment Without Downtime > Configuring rolling update strategy (score 0.682)

### m01 — по нескольким документам

**Вопрос:** Чем Deployment отличается от StatefulSet?

**Эталон:** Deployment управляет взаимозаменяемыми (stateless) Pod'ами и обеспечивает декларативные обновления. StatefulSet даёт каждому Pod стабильный уникальный сетевой идентификатор, стабильное постоянное хранилище и упорядоченные развёртывание, масштабирование и обновления — для stateful-приложений.

**Релевантные документы (all):** `concepts/workloads/controllers/deployment.md`, `concepts/workloads/controllers/statefulset.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1.   `concepts/workloads/controllers/_index.md` — Workload Management (score 0.690)
2.   `concepts/workloads/_index.md` — Workloads (score 0.672)
3. ✓ `concepts/workloads/controllers/statefulset.md` — StatefulSets > Using StatefulSets (score 0.628)
4. ✓ `concepts/workloads/controllers/statefulset.md` — StatefulSets (score 0.626)
5.   `tasks/run-application/run-replicated-stateful-application.md` — Run a Replicated Stateful Application > Deploy MySQL (score 0.611)

### m02 — по нескольким документам

**Вопрос:** Чем ConfigMap отличается от Secret?

**Эталон:** ConfigMap хранит несекретную конфигурацию в виде пар «ключ-значение» и не обеспечивает секретности или шифрования. Secret предназначен для небольших объёмов чувствительных данных — паролей, токенов, ключей.

**Релевантные документы (all):** `concepts/configuration/configmap.md`, `concepts/configuration/secret.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1. ✓ `concepts/configuration/configmap.md` — ConfigMaps (score 0.723)
2.   `concepts/security/security-checklist.md` — Security Checklist > Secrets (score 0.668)
3. ✓ `concepts/configuration/secret.md` — Secrets > Information security for Secrets (score 0.656)
4.   `tasks/configure-pod-container/configure-pod-configmap.md` — Configure a Pod to Use a ConfigMap > Understanding ConfigMaps and Pods (score 0.649)
5. ✓ `concepts/configuration/secret.md` — Secrets > Working with Secrets > Using Secrets with static Pods (score 0.649)

### m03 — по нескольким документам

**Вопрос:** Как связаны Deployment и ReplicaSet?

**Эталон:** ReplicaSet поддерживает заданное число одинаковых Pod'ов. Deployment — объект более высокого уровня, который управляет ReplicaSet'ами и даёт декларативные обновления (rolling update, откат), поэтому вместо прямого использования ReplicaSet рекомендуется Deployment.

**Релевантные документы (all):** `concepts/workloads/controllers/deployment.md`, `concepts/workloads/controllers/replicaset.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1. ✓ `concepts/workloads/controllers/replicaset.md` — ReplicaSet > Alternatives to ReplicaSet > Deployment (recommended) (score 0.731)
2. ✓ `concepts/workloads/controllers/replicaset.md` — ReplicaSet > When to use a ReplicaSet (score 0.721)
3.   `concepts/workloads/controllers/replicationcontroller.md` — ReplicationController > Alternatives to ReplicationController > ReplicaSet (score 0.699)
4.   `concepts/workloads/controllers/_index.md` — Workload Management (score 0.695)
5.   `concepts/workloads/_index.md` — Workloads (score 0.684)

### m04 — по нескольким документам

**Вопрос:** Чем DaemonSet отличается от Deployment?

**Эталон:** DaemonSet запускает копию Pod на всех (или выбранных) узлах и автоматически добавляет её на новые узлы. Deployment поддерживает заданное число реплик независимо от числа узлов.

**Релевантные документы (all):** `concepts/workloads/controllers/daemonset.md`, `concepts/workloads/controllers/deployment.md`

**Найдено (top-5 из 19):** retrieved 20 → score_threshold 20 → dedup 19 → min_length 19 → final 19
1. ✓ `concepts/workloads/controllers/daemonset.md` — DaemonSet > Alternatives to DaemonSet > Deployments (score 0.718)
2.   `concepts/workloads/_index.md` — Workloads (score 0.674)
3.   `concepts/workloads/controllers/_index.md` — Workload Management (score 0.644)
4.   `concepts/workloads/controllers/_index.md` — Workload Management (score 0.631)
5. ✓ `concepts/workloads/controllers/daemonset.md` — DaemonSet (score 0.628)

### m05 — по нескольким документам

**Вопрос:** Чем Job отличается от CronJob?

**Эталон:** Job создаёт Pod'ы и повторяет их выполнение, пока заданное число Pod'ов не завершится успешно. CronJob создаёт Job'ы по расписанию в формате cron.

**Релевантные документы (all):** `concepts/workloads/controllers/job.md`, `concepts/workloads/controllers/cron-jobs.md`

**Найдено (top-5 из 18):** retrieved 20 → score_threshold 20 → dedup 19 → min_length 18 → final 18
1. ✓ `concepts/workloads/controllers/cron-jobs.md` — CronJob (score 0.648)
2. ✓ `concepts/workloads/controllers/cron-jobs.md` — CronJob > CronJob limitations > Job creation (score 0.643)
3. ✓ `concepts/workloads/controllers/cron-jobs.md` — CronJob > CronJob limitations > Modifying a CronJob (score 0.636)
4. ✓ `concepts/workloads/controllers/job.md` — Jobs > Integrate with Workload APIs > CronJob behavior (score 0.636)
5. ✓ `concepts/workloads/controllers/cron-jobs.md` — CronJob > CronJob limitations > Job creation (score 0.628)

### m06 — по нескольким документам

**Вопрос:** Как StorageClass и PersistentVolumeClaim обеспечивают динамическое выделение томов?

**Эталон:** PersistentVolumeClaim — запрос пользователя на хранилище. Если в PVC указан StorageClass, его provisioner автоматически создаёт PersistentVolume по запросу (dynamic provisioning), и администратору не нужно создавать тома заранее.

**Релевантные документы (all):** `concepts/storage/persistent-volumes.md`, `concepts/storage/dynamic-provisioning.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1. ✓ `concepts/storage/dynamic-provisioning.md` — Dynamic Volume Provisioning > Using Dynamic Provisioning (score 0.656)
2.   `concepts/security/multi-tenancy.md` — Multi-tenancy > Data Plane Isolation > Storage isolation (score 0.655)
3.   `concepts/storage/storage-classes.md` — Storage Classes > StorageClass objects (score 0.653)
4.   `concepts/workloads/controllers/statefulset.md` — StatefulSets > Pod Identity > Stable Storage (score 0.651)
5.   `tutorials/stateful-application/mysql-wordpress-persistent-volume.md` — Example: Deploying WordPress and MySQL with Persistent Volumes > Create PersistentVolumeClaims and PersistentVolumes (score 0.651)

### m07 — по нескольким документам

**Вопрос:** Чем Ingress отличается от Service типа LoadBalancer?

**Эталон:** Service типа LoadBalancer публикует один Service наружу через внешний балансировщик нагрузки облака. Ingress маршрутизирует HTTP/HTTPS-трафик извне к разным Service по правилам (хосты, пути) и требует Ingress-контроллер.

**Релевантные документы (all):** `concepts/services-networking/ingress.md`, `concepts/services-networking/service.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1. ✓ `concepts/services-networking/ingress.md` — Ingress > Alternatives (score 0.661)
2. ✓ `concepts/services-networking/ingress.md` — Ingress > Types of Ingress > Load balancing (score 0.654)
3. ✓ `concepts/services-networking/service.md` — Service > Service type > `type: LoadBalancer` > Load balancer IP address mode (score 0.634)
4. ✓ `concepts/services-networking/ingress.md` — Ingress > Types of Ingress > Simple fanout (score 0.631)
5. ✓ `concepts/services-networking/ingress.md` — Ingress > What is Ingress? (score 0.614)

### c01 — понимание контекста

**Вопрос:** Когда стоит использовать StatefulSet, а не Deployment?

**Эталон:** Когда приложению нужны стабильные уникальные сетевые идентификаторы, стабильное постоянное хранилище и упорядоченные развёртывание, масштабирование и rolling update. Если этого не требуется, лучше подходит Deployment.

**Релевантные документы (any):** `concepts/workloads/controllers/statefulset.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1.   `concepts/workloads/controllers/_index.md` — Workload Management (score 0.727)
2. ✓ `concepts/workloads/controllers/statefulset.md` — StatefulSets > Using StatefulSets (score 0.713)
3.   `concepts/workloads/_index.md` — Workloads (score 0.696)
4. ✓ `concepts/workloads/controllers/statefulset.md` — StatefulSets (score 0.687)
5.   `tutorials/stateful-application/basic-stateful-set.md` — StatefulSet Basics > Objectives (score 0.673)

### c02 — понимание контекста

**Вопрос:** Что произойдёт с контейнером, если он попытается использовать больше памяти, чем его лимит?

**Эталон:** Контейнер становится кандидатом на завершение (OOM kill). Если он продолжает превышать лимит, его завершают, а при подходящей политике перезапуска kubelet перезапускает его.

**Релевантные документы (any):** `tasks/configure-pod-container/assign-memory-resource.md`, `concepts/configuration/manage-resources-containers.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1. ✓ `tasks/configure-pod-container/assign-memory-resource.md` — Assign Memory Resources to Containers and Pods > Exceed a Container's memory limit (score 0.736)
2. ✓ `concepts/configuration/manage-resources-containers.md` — Resource Management for Pods and Containers > Requests and limits (score 0.713)
3. ✓ `concepts/configuration/manage-resources-containers.md` — Resource Management for Pods and Containers > Requests and limits (score 0.685)
4. ✓ `concepts/configuration/manage-resources-containers.md` — Resource Management for Pods and Containers > How Kubernetes applies resource requests and limits (score 0.682)
5. ✓ `tasks/configure-pod-container/assign-memory-resource.md` — Assign Memory Resources to Containers and Pods > If you do not specify a memory limit (score 0.673)

### c03 — понимание контекста

**Вопрос:** Зачем нужны init-контейнеры?

**Эталон:** Это специальные контейнеры, которые выполняются до запуска основных контейнеров Pod — по очереди, каждый должен успешно завершиться. В них можно держать утилиты и скрипты подготовки, которых нет в образе приложения.

**Релевантные документы (any):** `concepts/workloads/pods/init-containers.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1. ✓ `concepts/workloads/pods/init-containers.md` — Init Containers > Using init containers (score 0.704)
2. ✓ `concepts/workloads/pods/init-containers.md` — Init Containers > Using init containers (score 0.700)
3. ✓ `concepts/workloads/pods/init-containers.md` — Init Containers > Understanding init containers (score 0.690)
4. ✓ `concepts/workloads/pods/init-containers.md` — Init Containers (score 0.682)
5. ✓ `concepts/workloads/pods/init-containers.md` — Init Containers > Using init containers > Examples (score 0.682)

### c04 — понимание контекста

**Вопрос:** Почему обычно не создают отдельные Pod'ы напрямую?

**Эталон:** Pod'ы эфемерны и одноразовые. Их лучше создавать через ресурсы рабочих нагрузок (Deployment, StatefulSet, Job), контроллеры которых пересоздают Pod'ы при сбоях, масштабируют их и выполняют обновления.

**Релевантные документы (any):** `concepts/workloads/pods/_index.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1. ✓ `concepts/workloads/pods/_index.md` — Pods > Working with Pods (score 0.677)
2. ✓ `concepts/workloads/pods/_index.md` — Pods > Using Pods > Workload resources for managing pods (score 0.640)
3.   `concepts/workloads/controllers/daemonset.md` — DaemonSet > Alternatives to DaemonSet > Bare Pods (score 0.620)
4. ✓ `concepts/workloads/pods/_index.md` — Pods (score 0.612)
5. ✓ `concepts/workloads/pods/_index.md` — Pods > Static Pods (score 0.609)

### c05 — понимание контекста

**Вопрос:** Что происходит, если readiness probe контейнера не проходит?

**Эталон:** Контейнер не перезапускается. IP-адрес Pod'а убирается из endpoints всех подходящих Service, и трафик на Pod не направляется, пока проба снова не начнёт проходить.

**Релевантные документы (any):** `concepts/workloads/pods/probes.md`, `concepts/workloads/pods/pod-lifecycle.md`

**Найдено (top-5 из 18):** retrieved 20 → score_threshold 20 → dedup 18 → min_length 18 → final 18
1. ✓ `concepts/workloads/pods/probes.md` — Liveness, Readiness, and Startup Probes > Configuration fields (score 0.679)
2. ✓ `concepts/workloads/pods/probes.md` — Liveness, Readiness, and Startup Probes > Probe results (score 0.674)
3. ✓ `concepts/workloads/pods/probes.md` — Liveness, Readiness, and Startup Probes > Types of probe > Readiness probe (score 0.659)
4.   `tasks/configure-pod-container/configure-liveness-readiness-startup-probes.md` — Configure Liveness, Readiness and Startup Probes > Define readiness probes (score 0.659)
5.   `tasks/run-application/run-replicated-stateful-application.md` — Run a Replicated Stateful Application > Simulate Pod and Node failure > Break the Readiness probe (score 0.642)

### c06 — понимание контекста

**Вопрос:** Для чего нужен PodDisruptionBudget?

**Эталон:** Он ограничивает число Pod'ов реплицированного приложения, которые могут быть одновременно недоступны из-за добровольных нарушений (например, drain узла при обслуживании), чтобы приложение оставалось доступным.

**Релевантные документы (any):** `concepts/workloads/pods/disruptions.md`, `tasks/run-application/configure-pdb.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1. ✓ `tasks/run-application/configure-pdb.md` — Specifying a Disruption Budget for your Application > Protecting an Application with a PodDisruptionBudget (score 0.709)
2. ✓ `tasks/run-application/configure-pdb.md` — Specifying a Disruption Budget for your Application > Specifying a PodDisruptionBudget (score 0.708)
3. ✓ `concepts/workloads/pods/disruptions.md` — Disruptions > Pod disruption budgets (score 0.701)
4.   `concepts/scheduling-eviction/pod-priority-preemption.md` — Pod Priority and Preemption > Preemption > Limitations of preemption > PodDisruptionBudget is supported, but not guaranteed (score 0.681)
5. ✓ `tasks/run-application/configure-pdb.md` — Specifying a Disruption Budget for your Application > Specifying a PodDisruptionBudget (score 0.675)

### c07 — понимание контекста

**Вопрос:** Почему Secret в Kubernetes по умолчанию нельзя считать надёжно защищённым?

**Эталон:** По умолчанию Secret хранится в etcd в незашифрованном виде, и любой, у кого есть доступ к API или etcd, может его прочитать. Нужно включить шифрование at rest и ограничить доступ через RBAC.

**Релевантные документы (any):** `concepts/configuration/secret.md`, `concepts/security/secrets-good-practices.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1. ✓ `concepts/configuration/secret.md` — Secrets (score 0.671)
2. ✓ `concepts/configuration/secret.md` — Secrets > Information security for Secrets (score 0.641)
3. ✓ `concepts/security/secrets-good-practices.md` — Good practices for Kubernetes Secrets > Cluster administrators > Configure encryption at rest (score 0.641)
4.   `concepts/security/hardening-guide/authentication-mechanisms.md` — Hardening Guide - Authentication Mechanisms > ServiceAccount secret tokens (score 0.639)
5. ✓ `concepts/configuration/secret.md` — Secrets (score 0.634)

### n01 — нет в базе

**Вопрос:** Как приготовить борщ?

**Эталон:** Ответа нет в документации — система должна отказаться.

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1.   `tasks/configure-pod-container/translate-compose-kubernetes.md` — Translate a Docker Compose File to Kubernetes Resources > Install Kompose (score 0.409)
2.   `tasks/configure-pod-container/translate-compose-kubernetes.md` — Translate a Docker Compose File to Kubernetes Resources > Use Kompose (score 0.385)
3.   `tasks/tools/install-kubectl-linux.md` — Install and Set Up kubectl on Linux > Optional kubectl configurations and plugins > Enable shell autocompletion (score 0.381)
4.   `tasks/job/coarse-parallel-processing-work-queue.md` — Coarse Parallel Processing Using a Work Queue > Testing the message queue service (score 0.379)
5.   `tasks/extend-kubernetes/setup-konnectivity.md` — Set up Konnectivity service > Before you begin (score 0.379)

### n02 — нет в базе

**Вопрос:** Кто выиграл чемпионат мира по футболу в 2018 году?

**Эталон:** Ответа нет в документации — система должна отказаться.

**Найдено (top-5 из 19):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 19 → final 19
1.   `concepts/overview/_index.md` — Overview (score 0.387)
2.   `tasks/debug/_index.md` — Monitoring, Logging, and Debugging > Help! My question isn't covered! I need help now! > Slack (score 0.385)
3.   `concepts/extend-kubernetes/compute-storage-net/device-plugins.md` — Device Plugins > Monitoring device plugin resources > `GetAllocatableResources` gRPC endpoint (score 0.337)
4.   `concepts/overview/_index.md` — Overview > What Kubernetes is not (score 0.336)
5.   `tutorials/kubernetes-basics/_index.md` — Learn Kubernetes Basics > What can Kubernetes do for you? (score 0.333)

### n03 — нет в базе

**Вопрос:** Сколько стоит управляемый кластер Kubernetes в Google Cloud в месяц?

**Эталон:** Ответа нет в документации — система должна отказаться.

**Найдено (top-5 из 19):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 19 → final 19
1.   `concepts/architecture/cloud-controller.md` — Cloud Controller Manager (score 0.580)
2.   `concepts/overview/_index.md` — Overview (score 0.568)
3.   `concepts/overview/components.md` — Kubernetes Components > Core Components > Control Plane Components (score 0.567)
4.   `concepts/security/multi-tenancy.md` — Multi-tenancy > Implementations (score 0.563)
5.   `tasks/administer-cluster/namespaces.md` — Share a Cluster with Namespaces > Viewing namespaces (score 0.558)

### n04 — нет в базе

**Вопрос:** В каком году Kubernetes передали в CNCF и кто был первым председателем технического комитета?

**Эталон:** Ответа нет в документации — система должна отказаться.

**Найдено (top-5 из 19):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 19 → final 19
1.   `concepts/overview/_index.md` — Overview (score 0.534)
2.   `concepts/security/cloud-native-security.md` — Cloud Native Security and Kubernetes (score 0.508)
3.   `concepts/security/controlling-access.md` — Controlling Access to the Kubernetes API > Transport security (score 0.486)
4.   `concepts/windows/_index.md` — Windows in Kubernetes (score 0.485)
5.   `tasks/debug/debug-cluster/_index.md` — Troubleshooting Clusters > Listing your cluster > Example: debugging a down/unreachable node (score 0.476)

### n05 — нет в базе

**Вопрос:** Как развернуть стек в Docker Swarm командой docker stack deploy?

**Эталон:** Ответа нет в документации — система должна отказаться.

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1.   `concepts/workloads/controllers/deployment.md` — Deployments > Creating a Deployment (score 0.529)
2.   `tasks/administer-cluster/migrating-from-dockershim/migrating-telemetry-and-security-agents.md` — Migrating telemetry and security agents from dockershim > Telemetry and security agents > Identify DaemonSets that depend on Docker Engine (score 0.518)
3.   `tasks/configure-pod-container/translate-compose-kubernetes.md` — Translate a Docker Compose File to Kubernetes Resources > Restart > Warning about Deployment Configurations (score 0.517)
4.   `tutorials/stateless-application/canary-deployment.md` — Deploy a Release Using a Canary Deployment > Deploying the canary version (score 0.513)
5.   `tutorials/stateless-application/canary-deployment.md` — Deploy a Release Using a Canary Deployment > Rolling back a canary deployment (score 0.511)

### n06 — нет в базе

**Вопрос:** Какая средняя зарплата DevOps-инженера в Москве?

**Эталон:** Ответа нет в документации — система должна отказаться.

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1.   `tasks/debug/debug-cluster/_index.md` — Troubleshooting Clusters > Listing your cluster > Example: debugging a down/unreachable node (score 0.437)
2.   `concepts/workloads/controllers/job.md` — Jobs > Writing a Job spec (score 0.426)
3.   `tasks/administer-cluster/kms-provider.md` — Using a KMS provider for data encryption > Implementing a KMS plugin > Developing a KMS plugin gRPC server > Notes > KMS v2 (score 0.420)
4.   `concepts/cluster-administration/dra.md` — Good practices for Dynamic Resource Allocation as a Cluster Admin > Monitor and tune components for higher load, especially in high scale environments > `kube-controller-manager` metrics (score 0.417)
5.   `concepts/cluster-administration/flow-control.md` — API Priority and Fairness > Resources > PriorityLevelConfiguration (score 0.416)

### n07 — нет в базе

**Вопрос:** Как собрать кластер Kubernetes на Raspberry Pi?

**Эталон:** Ответа нет в документации — система должна отказаться.

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1.   `tutorials/kubernetes-basics/create-cluster/cluster-intro.md` — Using Minikube to Create a Cluster > Kubernetes Clusters > Cluster Diagram (score 0.644)
2.   `tasks/administer-cluster/access-cluster-api.md` — Access Clusters Using the Kubernetes API > Accessing the Kubernetes API > Programmatic access to the API > Python client (score 0.640)
3.   `tutorials/stateless-application/expose-external-ip-address.md` — Exposing an External IP Address to Access an Application in a Cluster > Before you begin (score 0.639)
4.   `tasks/administer-cluster/kubelet-in-userns.md` — Running Kubernetes Node Components as a Non-root User > Manually deploy a node that runs the kubelet in a user namespace > Creating a user namespace (score 0.631)
5.   `tasks/administer-cluster/access-cluster-api.md` — Access Clusters Using the Kubernetes API > Accessing the Kubernetes API > Programmatic access to the API > dotnet client (score 0.623)

### n08 — нет в базе

**Вопрос:** Какое максимальное число узлов поддерживает один кластер Kubernetes?

**Эталон:** Ответа нет в корпусе (он есть только в разделе setup, не вошедшем в корпус) — система должна отказаться.

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → final 20
1.   `concepts/storage/storage-limits.md` — Node-specific Volume Limits > Kubernetes default limits (score 0.635)
2.   `concepts/services-networking/service.md` — Service > Defining a Service > Endpoints (deprecated) > Over-capacity endpoints (score 0.634)
3.   `concepts/policy/resource-quotas.md` — Resource Quotas > How Kubernetes ResourceQuotas work (score 0.622)
4.   `concepts/storage/storage-limits.md` — Node-specific Volume Limits > Dynamic volume limits (score 0.621)
5.   `tutorials/stateful-application/zookeeper.md` — Running ZooKeeper, A Distributed System Coordinator > Before you begin (score 0.611)
