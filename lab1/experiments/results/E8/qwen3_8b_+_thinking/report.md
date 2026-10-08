# Прогон `E8/qwen3_8b_+_thinking`

## Параметры

- `collection`: k8s__multilingual-e5-base__heading-1000-0-h
- `embedding_model`: multilingual-e5-base
- `chunking.strategy`: heading
- `chunking.chunk_size`: 1000
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
- `llm`: qwen3-8b-think
- `prompt`: strict
- `judge`: gemma3-12b-judge

## Retrieval (32 вопросов с ответом)

| K | Hit@K | Recall@K | Precision@K |
|--:|--:|--:|--:|
| 1 | 0.844 | 0.750 | 0.844 |
| 3 | 0.969 | 0.922 | 0.615 |
| 5 | 0.969 | 0.969 | 0.580 |
| 10 | 0.969 | 0.969 | 0.552 |
| 20 | 0.969 | 0.969 | 0.551 |

MRR: **0.901**

| Тип | Hit@5 | Recall@5 | MRR |
|---|--:|--:|--:|
| фактологические | 1.000 | 1.000 | 0.950 |
| поиск конкретики | 0.875 | 0.875 | 0.812 |
| по нескольким документам | 1.000 | 1.000 | 0.905 |
| понимание контекста | 1.000 | 1.000 | 0.929 |

Вопросы без ответа: контекст отсечён фильтрами в 75% случаев.
Вопросы с ответом: контекст отсечён целиком в 0% случаев.

## Генерация

- Отказ на вопросы без ответа (верно): **100%**
- Ложный отказ на вопросы с ответом: **0%**
- Источники ответа содержат релевантный документ: **97%**
- Вызовов LLM: 34 из 40

## Оценка судьи (0..1)

| Группа | Correctness | Faithfulness | Claim support | N |
|---|--:|--:|--:|--:|
| все вопросы | 0.838 | 0.984 | 0.996 | 40 |
| с ответом | 0.797 | 0.984 | 0.996 | 32 |
| фактологические | 0.950 | 1.000 | 1.000 | 10 |
| поиск конкретики | 0.812 | 1.000 | 1.000 | 8 |
| по нескольким документам | 0.643 | 0.928 | 0.982 | 7 |
| понимание контекста | 0.714 | 1.000 | 1.000 | 7 |
| нет в базе | 1.000 | — | — | 8 |

Correctness для вопросов без ответа: 1 — система отказалась. Faithfulness считается только для ответов, а не отказов.
Claim support — доля утверждений ответа, для которых судья нашёл цитату в контексте (как faithfulness в RAGAS).

Средняя задержка: retrieval 0.3095 с, generation 5.0522 с

## По вопросам

| id | Тип | Hit@5 | RR | Отказ | Correctness | Faithfulness |
|---|---|--:|--:|:-:|:-:|:-:|
| f01 | фактологические | 1.000 | 1.000 | нет | 2 ✓ | 2 ✓ |
| f02 | фактологические | 1.000 | 1.000 | нет | 2 ✓ | 2 ✓ |
| f03 | фактологические | 1.000 | 1.000 | нет | 2 ✓ | 2 ✓ |
| f04 | фактологические | 1.000 | 1.000 | нет | 2 ✓ | 2 ✓ |
| f05 | фактологические | 1.000 | 1.000 | нет | 2 ✓ | 2 ✓ |
| f06 | фактологические | 1.000 | 1.000 | нет | 2 ✓ | 2 ✓ |
| f07 | фактологические | 1.000 | 1.000 | нет | 2 ✓ | 2 ✓ |
| f08 | фактологические | 1.000 | 0.500 | нет | 1 ~ | 2 ✓ |
| f09 | фактологические | 1.000 | 1.000 | нет | 2 ✓ | 2 ✓ |
| f10 | фактологические | 1.000 | 1.000 | нет | 2 ✓ | 2 ✓ |
| s01 | поиск конкретики | 1.000 | 1.000 | нет | 2 ✓ | 2 ✓ |
| s02 | поиск конкретики | 1.000 | 0.500 | нет | 1 ~ | 2 ✓ |
| s03 | поиск конкретики | 1.000 | 1.000 | нет | 2 ✓ | 2 ✓ |
| s04 | поиск конкретики | 1.000 | 1.000 | нет | 1 ~ | 2 ✓ |
| s05 | поиск конкретики | 0.000 | 0.000 | нет | 2 ✓ | 2 ✓ |
| s06 | поиск конкретики | 1.000 | 1.000 | нет | 2 ✓ | 2 ✓ |
| s07 | поиск конкретики | 1.000 | 1.000 | нет | 2 ✓ | 2 ✓ |
| s08 | поиск конкретики | 1.000 | 1.000 | нет | 1 ~ | 2 ✓ |
| m01 | по нескольким документам | 1.000 | 0.333 | нет | 2 ✓ | 2 ✓ |
| m02 | по нескольким документам | 1.000 | 1.000 | нет | 1 ~ | 2 ✓ |
| m03 | по нескольким документам | 1.000 | 1.000 | нет | 1 ~ | 2 ✓ |
| m04 | по нескольким документам | 1.000 | 1.000 | нет | 1 ~ | 1 ~ |
| m05 | по нескольким документам | 1.000 | 1.000 | нет | 1 ~ | 2 ✓ |
| m06 | по нескольким документам | 1.000 | 1.000 | нет | 1 ~ | 2 ✓ |
| m07 | по нескольким документам | 1.000 | 1.000 | нет | 2 ✓ | 2 ✓ |
| c01 | понимание контекста | 1.000 | 1.000 | нет | 2 ✓ | 2 ✓ |
| c02 | понимание контекста | 1.000 | 1.000 | нет | 1 ~ | 2 ✓ |
| c03 | понимание контекста | 1.000 | 1.000 | нет | 1 ~ | 2 ✓ |
| c04 | понимание контекста | 1.000 | 1.000 | нет | 1 ~ | 2 ✓ |
| c05 | понимание контекста | 1.000 | 1.000 | нет | 1 ~ | 2 ✓ |
| c06 | понимание контекста | 1.000 | 0.500 | нет | 2 ✓ | 2 ✓ |
| c07 | понимание контекста | 1.000 | 1.000 | нет | 2 ✓ | 2 ✓ |
| n01 | нет в базе | — | — | да | 2 ✓ | — |
| n02 | нет в базе | — | — | да | 2 ✓ | — |
| n03 | нет в базе | — | — | да | 2 ✓ | — |
| n04 | нет в базе | — | — | да | 2 ✓ | — |
| n05 | нет в базе | — | — | да | 2 ✓ | — |
| n06 | нет в базе | — | — | да | 2 ✓ | — |
| n07 | нет в базе | — | — | да | 2 ✓ | — |
| n08 | нет в базе | — | — | да | 2 ✓ | — |

## Подробно

### f01 — фактологические

**Вопрос:** Что такое Pod?

**Эталон:** Pod — наименьшая развёртываемая единица вычислений в Kubernetes, группа из одного или нескольких контейнеров с общими хранилищем и сетевыми ресурсами и спецификацией их запуска.

**Релевантные документы (any):** `concepts/workloads/pods/_index.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 20 → final 20
1. ✓ `concepts/workloads/pods/_index.md` — Pods (score 0.840, rerank 0.999)
2.   `tutorials/kubernetes-basics/explore/explore-intro.md` — Viewing Pods and Nodes > Kubernetes Pods (score 0.817, rerank 0.992)
3. ✓ `concepts/workloads/pods/_index.md` — Pods > What is a Pod? (score 0.811, rerank 0.986)
4. ✓ `concepts/workloads/pods/_index.md` — Pods > What is a Pod? (score 0.826, rerank 0.981)
5.   `tutorials/kubernetes-basics/explore/explore-intro.md` — Viewing Pods and Nodes > Kubernetes Pods (score 0.800, rerank 0.974)

**Ответ:**

> Pod — это минимальная развертываемая единица в Kubernetes, представляющая группу одного или более контейнеров с общим сетевым и хранилищем, IP-адресом и спецификацией запуска [1]. Pod моделирует "логический хост" приложения, обеспечивая совместное размещение и расписание контейнеров [5]. В одном Pod могут быть контейнеры, тесно связанные и использующие общие ресурсы [3]. Pod управляется как единое целое, а не отдельные контейнеры [1].

**Источники:** [1] https://kubernetes.io/docs/concepts/workloads/pods/, [5] https://kubernetes.io/docs/tutorials/kubernetes-basics/explore/explore-intro/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы полностью передает ключевые факты об определении Pod, добавляя полезные детали о логическом хосте и управлении как единого целого. | Ответ точно отражает информацию из предоставленных фрагментов документации.

### f02 — фактологические

**Вопрос:** Какой компонент control plane хранит все данные кластера?

**Эталон:** etcd — согласованное высокодоступное хранилище «ключ-значение» для всех данных API-сервера.

**Релевантные документы (any):** `concepts/overview/components.md`

**Найдено (top-5 из 14):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 14 → final 14
1. ✓ `concepts/overview/components.md` — Kubernetes Components > Core Components > Control Plane Components (score 0.823, rerank 0.961)
2.   `tutorials/kubernetes-basics/create-cluster/cluster-intro.md` — Using Minikube to Create a Cluster > Kubernetes Clusters > Cluster Diagram (score 0.806, rerank 0.885)
3.   `concepts/security/multi-tenancy.md` — Multi-tenancy > Implementations > Virtual control plane per tenant (score 0.812, rerank 0.840)
4.   `tasks/administer-cluster/kubeadm/kubeadm-reconfigure.md` — Reconfiguring a kubeadm cluster > Persisting the reconfiguration > Persisting Node object reconfiguration > Persisting control plane component reconfiguration (score 0.804, rerank 0.825)
5.   `concepts/architecture/_index.md` — Cluster Architecture > Control plane components (score 0.818, rerank 0.815)

**Ответ:**

> Компонент control plane, который хранит все данные кластера, — это etcd [1]. Он выступает как распределённое хранилище ключ-значений, где сохраняются все данные API-сервера и состояние кластера.

**Источники:** [1] https://kubernetes.io/docs/concepts/overview/components/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы полностью соответствует эталонному и содержит все ключевые факты. | Ответ точно соответствует информации, представленной в фрагменте [1].

### f03 — фактологические

**Вопрос:** Какой порт обычно использует HTTP API kubelet на рабочих узлах?

**Эталон:** TCP-порт 10250.

**Релевантные документы (any):** `concepts/security/api-server-bypass-risks.md`

**Найдено (top-5 из 12):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 19 → rerank 12 → final 12
1. ✓ `concepts/security/api-server-bypass-risks.md` — Kubernetes API Server Bypass Risks > The kubelet API (score 0.863, rerank 0.998)
2.   `tutorials/cluster-management/kubelet-standalone.md` — Running Kubelet in Standalone Mode > Download, install, and configure the components > Download and set up the kubelet (score 0.832, rerank 0.957)
3.   `concepts/architecture/control-plane-node-communication.md` — Communication between Nodes and the Control Plane > Node to Control Plane (score 0.831, rerank 0.930)
4.   `concepts/security/controlling-access.md` — Controlling Access to the Kubernetes API > Transport security (score 0.847, rerank 0.760)
5.   `tutorials/cluster-management/kubelet-standalone.md` — Running Kubelet in Standalone Mode > Run a Pod in the kubelet > Find out information about the kubelet and the Pod (score 0.829, rerank 0.658)

**Ответ:**

> HTTP API kubelet на рабочих узлах обычно используется по порту 10250 [1]. Порт 10255 в фрагменте [5] относится к другому режиму (например, standalone) и не является основным для HTTP API.

**Источники:** [1] https://kubernetes.io/docs/concepts/security/api-server-bypass-risks/, [5] https://kubernetes.io/docs/tutorials/cluster-management/kubelet-standalone/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы точно указывает порт 10250 и правильно указывает на другой порт (10255) для другого режима. | Ответ точно отражает информацию из контекста, правильно выделяя основной порт и указывая на альтернативный режим.

### f04 — фактологические

**Вопрос:** Из какого диапазона по умолчанию выделяются порты для Service типа NodePort?

**Эталон:** Из диапазона 30000–32767.

**Релевантные документы (any):** `concepts/services-networking/service.md`

**Найдено (top-5 из 16):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 16 → final 16
1. ✓ `concepts/services-networking/service.md` — Service > Service type > `type: NodePort` (score 0.854, rerank 0.993)
2. ✓ `concepts/services-networking/service.md` — Service > Service type > `type: NodePort` > Reserve Nodeport ranges to avoid collisions (score 0.847, rerank 0.992)
3. ✓ `concepts/services-networking/service.md` — Service > Service type > `type: NodePort` > Choosing your own port (score 0.824, rerank 0.947)
4.   `tasks/access-application-cluster/create-external-load-balancer.md` — Create an External Load Balancer > Preserving the client source IP (score 0.808, rerank 0.767)
5.   `tutorials/services/source-ip.md` — Using Source IP > Source IP for Services with `Type=NodePort` (score 0.814, rerank 0.673)

**Ответ:**

> По умолчанию порты для Service типа NodePort выделяются из диапазона 30000-32767 [1, 2].

**Источники:** [1] https://kubernetes.io/docs/concepts/services-networking/service/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы полностью соответствует эталонному и содержит все ключевые факты. | Ответ точно соответствует информации, представленной в контексте.

### f05 — фактологические

**Вопрос:** Что делает kube-scheduler?

**Эталон:** Отслеживает Pod'ы, ещё не назначенные на узел, и выбирает для каждого из них подходящий узел.

**Релевантные документы (any):** `concepts/overview/components.md`, `concepts/scheduling-eviction/kube-scheduler.md`

**Найдено (top-5 из 19):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 19 → final 19
1. ✓ `concepts/scheduling-eviction/kube-scheduler.md` — Kubernetes Scheduler > kube-scheduler (score 0.876, rerank 0.998)
2.   `concepts/scheduling-eviction/scheduler-perf-tuning.md` — Scheduler Performance Tuning (score 0.870, rerank 0.996)
3. ✓ `concepts/scheduling-eviction/kube-scheduler.md` — Kubernetes Scheduler > kube-scheduler > Node selection in kube-scheduler (score 0.848, rerank 0.991)
4. ✓ `concepts/scheduling-eviction/kube-scheduler.md` — Kubernetes Scheduler > kube-scheduler (score 0.862, rerank 0.990)
5.   `concepts/cluster-administration/system-metrics.md` — Metrics For Kubernetes System Components > Component metrics > kube-scheduler metrics (score 0.842, rerank 0.989)

**Ответ:**

> kube-scheduler выбирает узел для запуска пода через два этапа: фильтрацию (нахождение подходящих узлов) и оценку (выбор узла с высшим рейтингом) [3]. Он учитывает ресурсы, политики, аффинность и другие факторы [4]. Если подходящих узлов нет, под остается несписанным [1]. После выбора узла scheduler уведомляет API-сервер о решении (binding) [2].

**Источники:** [1] https://kubernetes.io/docs/concepts/scheduling-eviction/kube-scheduler/, [2] https://kubernetes.io/docs/concepts/scheduling-eviction/scheduler-perf-tuning/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы верно описывает основные функции kube-scheduler, включая фильтрацию, оценку и уведомление API-сервера. | Ответ точно отражает информацию из предоставленного контекста и дает краткое, но полное описание работы kube-scheduler.

### f06 — фактологические

**Вопрос:** Какое значение restartPolicy у Pod используется по умолчанию?

**Эталон:** Always.

**Релевантные документы (any):** `concepts/workloads/pods/pod-lifecycle.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 20 → final 20
1. ✓ `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > How Pods handle problems with containers > Container restarts > Pod-level container restart policy (score 0.869, rerank 0.995)
2.   `tutorials/stateful-application/zookeeper.md` — Running ZooKeeper, A Distributed System Coordinator > Managing the ZooKeeper process > Handling process failure (score 0.850, rerank 0.990)
3. ✓ `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > How Pods handle problems with containers > Container restarts > Restart All Containers > How in-place Pod restarts work (score 0.863, rerank 0.978)
4. ✓ `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > How Pods handle problems with containers > Container restarts > Pod-level container restart policy > Restart behavior comparison (score 0.858, rerank 0.969)
5.   `concepts/workloads/pods/init-containers.md` — Init Containers > Detailed behavior (score 0.850, rerank 0.917)

**Ответ:**

> По умолчанию значение `restartPolicy` для Pod — `Always` [1]. Это значение также подтверждается в разделе о поведении Deployments, где указано, что они используют `restartPolicy: Always` как единственное допустимое значение по умолчанию [4].

**Источники:** [1] https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы полностью соответствует эталонному и даже добавляет информацию о Deployments. | Ответ точно соответствует контексту и предоставляет подтверждающие фрагменты.

### f07 — фактологические

**Вопрос:** Какой максимальный объём данных можно хранить в одном ConfigMap?

**Эталон:** Не более 1 MiB.

**Релевантные документы (any):** `concepts/configuration/configmap.md`

**Найдено (top-5 из 6):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 6 → final 6
1. ✓ `concepts/configuration/configmap.md` — ConfigMaps > Motivation (score 0.826, rerank 0.989)
2. ✓ `concepts/configuration/configmap.md` — ConfigMaps > ConfigMaps and Pods (score 0.813, rerank 0.441)
3.   `tutorials/configuration/configure-redis-using-configmap.md` — Configuring Redis using a ConfigMap > Real World Example: Configuring Redis using a ConfigMap (score 0.799, rerank 0.395)
4.   `concepts/storage/volumes.md` — Volumes > Types of volumes > configMap (score 0.805, rerank 0.231)
5.   `tutorials/configuration/configure-redis-using-configmap.md` — Configuring Redis using a ConfigMap > Real World Example: Configuring Redis using a ConfigMap (score 0.806, rerank 0.139)

**Ответ:**

> Максимальный объем данных, который можно хранить в одном ConfigMap, составляет 1 MiB [1].

**Источники:** [1] https://kubernetes.io/docs/concepts/configuration/configmap/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы полностью соответствует эталонному и содержит правильный объём данных. | Ответ точно соответствует информации, представленной в контексте.

### f08 — фактологические

**Вопрос:** Для чего в Kubernetes нужны Namespace?

**Эталон:** Namespace — механизм изоляции групп ресурсов внутри одного кластера; имена ресурсов должны быть уникальны в пределах namespace, но не между namespace.

**Релевантные документы (any):** `concepts/overview/working-with-objects/namespaces.md`

**Найдено (top-5 из 16):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 16 → final 16
1.   `concepts/security/multi-tenancy.md` — Multi-tenancy > Control plane isolation > Namespaces (score 0.865, rerank 0.992)
2. ✓ `concepts/overview/working-with-objects/namespaces.md` — Namespaces > When to Use Multiple Namespaces (score 0.858, rerank 0.990)
3. ✓ `concepts/overview/working-with-objects/namespaces.md` — Namespaces (score 0.865, rerank 0.974)
4.   `tasks/administer-cluster/namespaces.md` — Share a Cluster with Namespaces > Understanding the motivation for using namespaces (score 0.852, rerank 0.949)
5.   `concepts/security/multi-tenancy.md` — Multi-tenancy > Implementations (score 0.850, rerank 0.896)

**Ответ:**

> Namespaces в Kubernetes нужны для изоляции групп ресурсов в одном кластере [1], разделения ресурсов между пользователями или командами [4], обеспечения уникальности имен ресурсов внутри каждого пространства имен [3], а также применения политик безопасности (RBAC, Network Policies) и квот [1, 2]. Они позволяют разным пользователям/командам работать изолированно, но при этом использовать общий кластер [4]. Однако Namespaces не подходят для ресурсов, которые не могут быть разнесены по пространствам имен, например, StorageClass или Custom Resource Definitions [5].

**Источники:** [1] https://kubernetes.io/docs/concepts/security/multi-tenancy/, [2] https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/, [4] https://kubernetes.io/docs/tasks/administer-cluster/namespaces/

**Оценка:** correctness 1 ~, faithfulness 2 ✓. Ответ системы верно описывает изоляцию ресурсов и уникальность имен внутри namespace, но не упоминает об уникальности имен между namespace, что является важной частью определения. | Ответ точно отражает информацию из предоставленного контекста и охватывает основные аспекты использования Namespaces.

### f09 — фактологические

**Вопрос:** Что означает фаза Pending у Pod?

**Эталон:** Pod принят кластером, но один или несколько контейнеров ещё не готовы к запуску — в том числе Pod ждёт планирования на узел или загрузки образов.

**Релевантные документы (any):** `concepts/workloads/pods/pod-lifecycle.md`

**Найдено (top-5 из 11):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 11 → final 11
1. ✓ `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > Pod phase (score 0.851, rerank 0.996)
2. ✓ `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle (score 0.826, rerank 0.963)
3.   `tasks/debug/debug-application/debug-pods.md` — Debug Pods > Diagnosing the problem > Debugging Pods > My pod stays pending (score 0.839, rerank 0.937)
4. ✓ `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > Pod phase (score 0.833, rerank 0.768)
5. ✓ `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > Pod phase (score 0.843, rerank 0.370)

**Ответ:**

> Фаза `Pending` означает, что Pod принят кластером Kubernetes, но контейнеры еще не готовы к запуску [1]. Это может включать ожидание расписания или загрузку образов контейнеров [1]. Также Pod может оставаться в этом состоянии, если не удается распределить его на узел из-за недостатка ресурсов [3].

**Источники:** [1] https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/, [3] https://kubernetes.io/docs/tasks/debug/debug-application/debug-pods/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы полностью соответствует эталонному, включая причину задержки - нехватку ресурсов. | Ответ точно отражает информацию из предоставленного контекста и не содержит выдуманных деталей.

### f10 — фактологические

**Вопрос:** Какой тип Service создаётся, если тип не указан явно?

**Эталон:** ClusterIP.

**Релевантные документы (any):** `concepts/services-networking/service.md`

**Найдено (top-5 из 3):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 3 → final 3
1. ✓ `concepts/services-networking/service.md` — Service > Service type (score 0.793, rerank 0.605)
2. ✓ `concepts/services-networking/service.md` — Service > Headless Services > Without selectors (score 0.795, rerank 0.201)
3.   `tutorials/kubernetes-basics/expose/expose-intro.md` — Using a Service to Expose Your App > Overview of Kubernetes Services (score 0.813, rerank 0.168)

**Ответ:**

> Если тип Service не указан явно, создаётся Service типа `ClusterIP` [1]. Это значение используется по умолчанию, так как Kubernetes автоматически назначает внутренний IP-адрес для сервиса.

**Источники:** [1] https://kubernetes.io/docs/concepts/services-networking/service/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы точно и полно передает информацию об использовании типа ClusterIP по умолчанию при отсутствии явного указания типа Service. | Ответ точно соответствует контексту, четко указывая тип `ClusterIP` как значение по умолчанию.

### s01 — поиск конкретики

**Вопрос:** Какое поле манифеста Deployment задаёт желаемое число реплик?

**Эталон:** Поле `.spec.replicas`.

**Релевантные документы (any):** `concepts/workloads/controllers/deployment.md`

**Найдено (top-5 из 14):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 19 → rerank 14 → final 14
1. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Writing a Deployment Spec > Replicas (score 0.842, rerank 0.991)
2. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Creating a Deployment (score 0.827, rerank 0.974)
3.   `tutorials/kubernetes-basics/scale/scale-intro.md` — Running Multiple Instances of Your App > Scaling overview > Scaling a Deployment (score 0.809, rerank 0.907)
4. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Updating a Deployment (score 0.820, rerank 0.793)
5.   `tutorials/cluster-management/admission-policies.md` — Explore Validating and Mutating Admission Policies > Enforcement through validation (score 0.817, rerank 0.754)

**Ответ:**

> Поле `.spec.replicas` в манифесте Deployment задаёт желаемое число реплик [1].

**Источники:** [1] https://kubernetes.io/docs/concepts/workloads/controllers/deployment/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы полностью соответствует эталонному и точно указывает поле манифеста Deployment, определяющее желаемое число реплик. | Ответ содержит только одно утверждение, которое полностью подтверждается контекстом.

### s02 — поиск конкретики

**Вопрос:** Какой командой kubectl изменить число реплик Deployment?

**Эталон:** `kubectl scale deployment/<имя> --replicas=<N>`, например `kubectl scale deployment/nginx-deployment --replicas=10`.

**Релевантные документы (any):** `concepts/workloads/controllers/deployment.md`, `tutorials/kubernetes-basics/scale/scale-intro.md`

**Найдено (top-5 из 18):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 18 → final 18
1.   `tasks/run-application/scale-deployment.md` — Horizontal Manual Scaling for a Deployment > Other ways to change the replica count > Scale using `kubectl patch` (score 0.854, rerank 0.997)
2. ✓ `tutorials/kubernetes-basics/scale/scale-intro.md` — Running Multiple Instances of Your App > Scaling overview > Scaling a Deployment (score 0.857, rerank 0.993)
3.   `tasks/manage-kubernetes-objects/update-api-object-kubectl-patch.md` — Update API Objects in Place Using kubectl patch > Use strategic merge patch to update a Deployment using the retainKeys strategy > Update an object's replica count using `kubectl patch` with `--subresource` (score 0.862, rerank 0.985)
4.   `tasks/run-application/scale-deployment.md` — Horizontal Manual Scaling for a Deployment > Other ways to change the replica count > Scale using `kubectl edit` (score 0.852, rerank 0.984)
5. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Updating a Deployment (score 0.853, rerank 0.964)

**Ответ:**

> Чтобы изменить число реплик Deployment, можно использовать следующие команды:  
> - `kubectl scale deployments/<name> --replicas=<number>` [2],  
> - `kubectl patch deployment <name> -p '{"spec":{"replicas":<number>}}'` [1],  
> - `kubectl edit deployment <name>` (изменить `.spec.replicas` вручную) [4].  
> Для проверки изменений используйте `kubectl get deployments` или `kubectl get pods`.

**Источники:** [1] https://kubernetes.io/docs/tasks/run-application/scale-deployment/, [2] https://kubernetes.io/docs/tutorials/kubernetes-basics/scale/scale-intro/

**Оценка:** correctness 1 ~, faithfulness 2 ✓. Ответ системы предоставляет несколько способов изменения числа реплик, включая `kubectl scale`, но не упоминает пример использования, как в эталонном ответе, и добавляет команды для проверки, которые не были запрошены. | Ответ точно соответствует контексту и перечисляет все предложенные способы изменения числа реплик.

### s03 — поиск конкретики

**Вопрос:** Какой командой откатить Deployment на предыдущую ревизию?

**Эталон:** `kubectl rollout undo deployment/<имя>`; с `--to-revision=<N>` — на конкретную ревизию.

**Релевантные документы (any):** `concepts/workloads/controllers/deployment.md`, `tasks/run-application/update-deployment-rolling.md`, `tutorials/kubernetes-basics/update/update-intro.md`

**Найдено (top-5 из 6):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 6 → final 6
1. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Rolling Back a Deployment > Rolling Back to a Previous Revision (score 0.816, rerank 0.993)
2. ✓ `tasks/run-application/update-deployment-rolling.md` — Update a Deployment Without Downtime > Rolling back to a previous revision > Rolling back to a specific revision (score 0.817, rerank 0.932)
3. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Writing a Deployment Spec > Strategy > Recreate Deployment (score 0.817, rerank 0.626)
4. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Rolling Back a Deployment > Rolling Back to a Previous Revision (score 0.816, rerank 0.622)
5. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Writing a Deployment Spec > Revision History Limit (score 0.826, rerank 0.236)

**Ответ:**

> Чтобы откатить Deployment на предыдущую ревизию, используйте команду `kubectl rollout undo deployment/nginx-deployment --to-revision=<номер_ревизии>` [1, 2]. Если не указать `--to-revision`, откатится на последнюю доступную ревизию [1].

**Источники:** [1] https://kubernetes.io/docs/concepts/workloads/controllers/deployment/, [2] https://kubernetes.io/docs/tasks/run-application/update-deployment-rolling/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы полностью соответствует эталонному, включая пример команды и объяснение поведения при отсутствии флага --to-revision. | Оба утверждения точно соответствуют информации, представленной в контексте.

### s04 — поиск конкретики

**Вопрос:** Какое поле в манифесте контейнера задаёт лимит памяти?

**Эталон:** `resources.limits.memory` (минимальный запрос памяти — `resources.requests.memory`).

**Релевантные документы (any):** `tasks/configure-pod-container/assign-memory-resource.md`, `concepts/configuration/manage-resources-containers.md`

**Найдено (top-5 из 15):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 15 → final 15
1. ✓ `tasks/configure-pod-container/assign-memory-resource.md` — Assign Memory Resources to Containers and Pods > Specify a memory request and a memory limit (score 0.835, rerank 0.990)
2.   `tasks/configure-pod-container/assign-pod-level-resources.md` — Assign Pod-level CPU and memory resources > Create a pod with memory requests and limits at pod-level (score 0.826, rerank 0.930)
3.   `tasks/administer-cluster/manage-resources/memory-default-namespace.md` — Configure Default Memory Requests and Limits for a Namespace > What if you specify a container's request, but not its limit? (score 0.837, rerank 0.911)
4.   `tasks/administer-cluster/manage-resources/memory-constraint-namespace.md` — Configure Minimum and Maximum Memory Constraints for a Namespace > Create a Pod that does not specify any memory request or limit (score 0.827, rerank 0.859)
5.   `tasks/administer-cluster/manage-resources/memory-constraint-namespace.md` — Configure Minimum and Maximum Memory Constraints for a Namespace > Create a LimitRange and a Pod (score 0.834, rerank 0.830)

**Ответ:**

> В манифесте контейнера лимит памяти задаётся полем `resources.limits.memory` [1, 2, 3, 4, 5].

**Источники:** [1] https://kubernetes.io/docs/tasks/configure-pod-container/assign-memory-resource/, [2] https://kubernetes.io/docs/tasks/configure-pod-container/assign-pod-level-resources/, [3] https://kubernetes.io/docs/tasks/administer-cluster/manage-resources/memory-default-namespace/, [4] https://kubernetes.io/docs/tasks/administer-cluster/manage-resources/memory-constraint-namespace/

**Оценка:** correctness 1 ~, faithfulness 2 ✓. Ответ системы верно указывает поле для лимита памяти, но не упоминает минимальный запрос памяти. | Все утверждения точно соответствуют информации, представленной в предоставленных фрагментах документации.

### s05 — поиск конкретики

**Вопрос:** Какое поле Pod — самый простой рекомендуемый способ ограничить узлы, на которых он может запускаться, по меткам узлов?

**Эталон:** Поле `nodeSelector`.

**Релевантные документы (any):** `concepts/scheduling-eviction/assign-pod-node.md`

**Найдено (top-5 из 5):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 5 → final 5
1.   `concepts/scheduling-eviction/topology-spread-constraints.md` — Pod Topology Spread Constraints > `topologySpreadConstraints` field (score 0.829, rerank 0.152)
2.   `concepts/security/security-checklist.md` — Security Checklist > Pod security (score 0.839, rerank 0.140)
3.   `tasks/administer-cluster/securing-a-cluster.md` — Securing a Cluster > Controlling the capabilities of a workload or user at runtime > Controlling which nodes pods may access (score 0.822, rerank 0.133)
4.   `concepts/workloads/controllers/job.md` — Jobs > Advanced usage > Mutable Scheduling Directives (score 0.823, rerank 0.118)
5.   `concepts/security/pod-security-standards.md` — Pod Security Standards > Pod OS field (score 0.822, rerank 0.107)

**Ответ:**

> Самый простой рекомендуемый способ — использование поля `nodeSelector` в `PodSpec` [3]. Это позволяет явно указать метки узлов, на которых может запускаться Pod, ограничивая его распределение по кластеру.

**Источники:** [3] https://kubernetes.io/docs/tasks/administer-cluster/securing-a-cluster/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы точно и полно передает ключевые факты эталонного ответа. | Ответ правильно определяет `nodeSelector` как рекомендуемый способ и подкрепляет это ссылкой на соответствующий фрагмент документации.

### s06 — поиск конкретики

**Вопрос:** Какие три вида проб (probes) можно настроить для контейнера?

**Эталон:** Liveness probe, readiness probe и startup probe.

**Релевантные документы (any):** `concepts/workloads/pods/probes.md`, `tasks/configure-pod-container/configure-liveness-readiness-startup-probes.md`

**Найдено (top-5 из 16):** retrieved 20 → score_threshold 20 → dedup 19 → min_length 19 → rerank 16 → final 16
1. ✓ `concepts/workloads/pods/probes.md` — Liveness, Readiness, and Startup Probes > Types of probe (score 0.841, rerank 0.975)
2.   `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > Container probes (score 0.819, rerank 0.914)
3. ✓ `tasks/configure-pod-container/configure-liveness-readiness-startup-probes.md` — Configure Liveness, Readiness and Startup Probes > Define a TCP liveness probe (score 0.818, rerank 0.746)
4. ✓ `tasks/configure-pod-container/configure-liveness-readiness-startup-probes.md` — Configure Liveness, Readiness and Startup Probes (score 0.818, rerank 0.730)
5. ✓ `concepts/workloads/pods/probes.md` — Liveness, Readiness, and Startup Probes > Types of probe > Startup probe (score 0.812, rerank 0.678)

**Ответ:**

> Контейнер можно настроить для использования трех типов проб: startup, liveness и readiness [1]. Эти пробы используются для мониторинга состояния приложения внутри контейнера [2]. Каждый тип пробы выполняет разные задачи: startup — проверяет запуск приложения, liveness — определяет жизнеспособность контейнера, readiness — проверяет готовность контейнера к обработке трафика [1, 5].

**Источники:** [1] https://kubernetes.io/docs/concepts/workloads/pods/probes/, [2] https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы перечисляет все три типа проб и кратко описывает их назначение, что соответствует эталонному ответу. | Ответ точно отражает информацию из предоставленного контекста и правильно идентифицирует три типа проб.

### s07 — поиск конкретики

**Вопрос:** Какой командой посмотреть логи предыдущего (упавшего) экземпляра контейнера?

**Эталон:** `kubectl logs <pod> -c <контейнер> --previous`.

**Релевантные документы (any):** `tasks/debug/debug-application/debug-running-pod.md`, `concepts/cluster-administration/logging.md`

**Найдено (top-5 из 4):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 4 → final 4
1. ✓ `tasks/debug/debug-application/debug-running-pod.md` — Debug Running Pods > Examining pod logs (score 0.814, rerank 0.988)
2. ✓ `concepts/cluster-administration/logging.md` — Logging Architecture > Pod and container logs (score 0.793, rerank 0.944)
3.   `tutorials/stateful-application/zookeeper.md` — Running ZooKeeper, A Distributed System Coordinator > Ensuring consistent configuration > Configuring logging (score 0.794, rerank 0.198)
4.   `tasks/inject-data-application/downward-api-volume-expose-pod-information.md` — Expose Pod Information to Containers Through Files > Store Pod fields (score 0.795, rerank 0.139)

**Ответ:**

> Чтобы посмотреть логи предыдущего (упавшего) экземпляра контейнера, используйте команду:  
> ```shell
> kubectl logs ${POD_NAME} -c ${CONTAINER_NAME} --previous
> ```  
> Это позволяет получить логи из предыдущего запуска контейнера, если он завершился [1], [2].

**Источники:** [1] https://kubernetes.io/docs/tasks/debug/debug-application/debug-running-pod/, [2] https://kubernetes.io/docs/concepts/cluster-administration/logging/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы полностью соответствует эталонному, включая все ключевые компоненты команды. | Ответ точно соответствует контексту и предоставляет правильную команду.

### s08 — поиск конкретики

**Вопрос:** Какой параметр rolling update задаёт, сколько Pod'ов может быть недоступно во время обновления Deployment?

**Эталон:** `maxUnavailable` (`.spec.strategy.rollingUpdate.maxUnavailable`): число или процент Pod'ов; по умолчанию 25%.

**Релевантные документы (any):** `concepts/workloads/controllers/deployment.md`, `tasks/run-application/update-deployment-rolling.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 20 → final 20
1. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Writing a Deployment Spec > Strategy > Rolling Update Deployment > Max Unavailable (score 0.883, rerank 0.998)
2. ✓ `tasks/run-application/update-deployment-rolling.md` — Update a Deployment Without Downtime > Configuring rolling update strategy (score 0.869, rerank 0.996)
3.   `concepts/workloads/controllers/statefulset.md` — StatefulSets > Rolling Updates > Maximum unavailable Pods (score 0.864, rerank 0.988)
4. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Writing a Deployment Spec > Strategy > Rolling Update Deployment > Max Surge (score 0.865, rerank 0.985)
5.   `tutorials/kubernetes-basics/update/update-intro.md` — Performing a Rolling Update > Updating an application (score 0.868, rerank 0.981)

**Ответ:**

> Параметр `maxUnavailable` задаёт максимальное количество Pod'ов, которые могут быть недоступны во время rolling update. Он может быть указан как абсолютное число или процент от желаемого количества Pod'ов [1, 2, 4].

**Источники:** [1] https://kubernetes.io/docs/concepts/workloads/controllers/deployment/, [2] https://kubernetes.io/docs/tasks/run-application/update-deployment-rolling/

**Оценка:** correctness 1 ~, faithfulness 2 ✓. Ответ системы верно описывает назначение и возможные типы значений параметра `maxUnavailable`, но не упоминает значение по умолчанию. | Ответ точно отражает информацию из предоставленного контекста и не содержит выдуманных деталей.

### m01 — по нескольким документам

**Вопрос:** Чем Deployment отличается от StatefulSet?

**Эталон:** Deployment управляет взаимозаменяемыми (stateless) Pod'ами и обеспечивает декларативные обновления. StatefulSet даёт каждому Pod стабильный уникальный сетевой идентификатор, стабильное постоянное хранилище и упорядоченные развёртывание, масштабирование и обновления — для stateful-приложений.

**Релевантные документы (all):** `concepts/workloads/controllers/deployment.md`, `concepts/workloads/controllers/statefulset.md`

**Найдено (top-5 из 16):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 19 → rerank 16 → final 16
1.   `concepts/workloads/controllers/_index.md` — Workload Management (score 0.876, rerank 0.998)
2.   `concepts/workloads/_index.md` — Workloads (score 0.858, rerank 0.985)
3. ✓ `concepts/workloads/controllers/statefulset.md` — StatefulSets > Using StatefulSets (score 0.856, rerank 0.938)
4. ✓ `concepts/workloads/controllers/deployment.md` — Deployments (score 0.838, rerank 0.802)
5. ✓ `concepts/workloads/controllers/statefulset.md` — StatefulSets > Deployment and Scaling Guarantees (score 0.837, rerank 0.699)

**Ответ:**

> Deployment используется для управления безсостоятельными приложениями с взаимозаменяемыми Pod'ами [1], а StatefulSet — для приложений с уникальной идентичностью и зависимостью от постоянного хранилища [1]. Deployment обеспечивает декларативные обновления и масштабирование без порядка [4], в то время как StatefulSet гарантирует упорядоченное развертывание, удаление и масштабирование с учетом зависимости между Pod'ами [5]. StatefulSet также предоставляет стабильные сетевые идентификаторы и PersistentVolume для каждого Pod [3].

**Источники:** [1] https://kubernetes.io/docs/concepts/workloads/controllers/, [3] https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/, [4] https://kubernetes.io/docs/concepts/workloads/controllers/deployment/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы верно описывает ключевые отличия Deployment и StatefulSet, включая управление stateless/stateful приложениями, упорядоченность, сетевые идентификаторы и постоянное хранилище. | Ответ точно отражает различия между Deployment и StatefulSet, основываясь на предоставленном контексте.

### m02 — по нескольким документам

**Вопрос:** Чем ConfigMap отличается от Secret?

**Эталон:** ConfigMap хранит несекретную конфигурацию в виде пар «ключ-значение» и не обеспечивает секретности или шифрования. Secret предназначен для небольших объёмов чувствительных данных — паролей, токенов, ключей.

**Релевантные документы (all):** `concepts/configuration/configmap.md`, `concepts/configuration/secret.md`

**Найдено (top-5 из 15):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 15 → final 15
1. ✓ `concepts/configuration/secret.md` — Secrets (score 0.856, rerank 0.987)
2.   `concepts/configuration/_index.md` — Configuration > Kubernetes configuration-related APIs > Secrets (score 0.849, rerank 0.984)
3.   `tasks/configure-pod-container/configure-pod-configmap.md` — Configure a Pod to Use a ConfigMap > Understanding ConfigMaps and Pods (score 0.842, rerank 0.979)
4. ✓ `concepts/configuration/configmap.md` — ConfigMaps (score 0.859, rerank 0.979)
5. ✓ `concepts/configuration/secret.md` — Secrets > Information security for Secrets (score 0.830, rerank 0.970)

**Ответ:**

> ConfigMap и Secret отличаются назначением и защитой. ConfigMap хранит нечувствительные данные в виде ключ-значение (например, конфигурации) [3], а Secret предназначен для конфиденциальной информации, такой как пароли или токены [1]. Secret имеет дополнительные меры безопасности: Kubernetes ограничивает доступ к данным и избегает их записи в неvolatile-память [1, 5]. ConfigMap не обеспечивает секретности и не шифрует данные, поэтому для конфиденциальной информации следует использовать Secret [4].

**Источники:** [1] https://kubernetes.io/docs/concepts/configuration/secret/, [3] https://kubernetes.io/docs/tasks/configure-pod-container/configure-pod-configmap/, [4] https://kubernetes.io/docs/concepts/configuration/configmap/

**Оценка:** correctness 1 ~, faithfulness 2 ✓. Ответ системы верно описывает назначение и некоторые аспекты безопасности ConfigMap и Secret, но не упоминает, что Secret предназначен для *небольших* объемов данных. | Ответ точно отражает информацию из предоставленного контекста и корректно описывает различия между ConfigMap и Secret.

### m03 — по нескольким документам

**Вопрос:** Как связаны Deployment и ReplicaSet?

**Эталон:** ReplicaSet поддерживает заданное число одинаковых Pod'ов. Deployment — объект более высокого уровня, который управляет ReplicaSet'ами и даёт декларативные обновления (rolling update, откат), поэтому вместо прямого использования ReplicaSet рекомендуется Deployment.

**Релевантные документы (all):** `concepts/workloads/controllers/deployment.md`, `concepts/workloads/controllers/replicaset.md`

**Найдено (top-5 из 19):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 19 → final 19
1. ✓ `concepts/workloads/controllers/replicaset.md` — ReplicaSet > Alternatives to ReplicaSet > Deployment (recommended) (score 0.884, rerank 0.995)
2. ✓ `concepts/workloads/controllers/replicaset.md` — ReplicaSet > When to use a ReplicaSet (score 0.879, rerank 0.993)
3. ✓ `concepts/workloads/controllers/deployment.md` — Deployments (score 0.856, rerank 0.992)
4. ✓ `concepts/workloads/controllers/deployment.md` — Deployments > Updating a Deployment > Rollover (aka multiple updates in-flight) (score 0.832, rerank 0.982)
5.   `concepts/workloads/controllers/replicationcontroller.md` — ReplicationController > Alternatives to ReplicationController > ReplicaSet (score 0.871, rerank 0.980)

**Ответ:**

> Deployment управляет ReplicaSet, создавая и обновляя их для обеспечения нужного количества реплик [1]. Deployment использует ReplicaSet как механизм для orchestration создания, удаления и обновления Pod [2]. При обновлениях Deployment создает новые ReplicaSet, уменьшая старые и перенося их в список устаревших [4]. ReplicaSet主要用于 Deployment для управления состоянием Pod, но не рекомендуется управлять ими напрямую, если не требуется кастомное обновление [5].

**Источники:** [1] https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/, [4] https://kubernetes.io/docs/concepts/workloads/controllers/deployment/, [5] https://kubernetes.io/docs/concepts/workloads/controllers/replicationcontroller/

**Оценка:** correctness 1 ~, faithfulness 2 ✓. Ответ системы верно описывает связь между Deployment и ReplicaSet, но не упоминает напрямую rolling update и откаты, хотя и подразумевает это, говоря о создании новых ReplicaSet при обновлениях. | Ответ точно отражает информацию из предоставленных фрагментов документации.

### m04 — по нескольким документам

**Вопрос:** Чем DaemonSet отличается от Deployment?

**Эталон:** DaemonSet запускает копию Pod на всех (или выбранных) узлах и автоматически добавляет её на новые узлы. Deployment поддерживает заданное число реплик независимо от числа узлов.

**Релевантные документы (all):** `concepts/workloads/controllers/daemonset.md`, `concepts/workloads/controllers/deployment.md`

**Найдено (top-5 из 12):** retrieved 20 → score_threshold 20 → dedup 19 → min_length 19 → rerank 12 → final 12
1. ✓ `concepts/workloads/controllers/daemonset.md` — DaemonSet > Alternatives to DaemonSet > Deployments (score 0.878, rerank 0.997)
2.   `concepts/workloads/_index.md` — Workloads (score 0.850, rerank 0.986)
3. ✓ `concepts/workloads/controllers/deployment.md` — Deployments (score 0.824, rerank 0.692)
4.   `concepts/extend-kubernetes/compute-storage-net/device-plugins.md` — Device Plugins > Device plugin deployment (score 0.832, rerank 0.546)
5.   `concepts/workloads/controllers/_index.md` — Workload Management (score 0.837, rerank 0.531)

**Ответ:**

> DaemonSet гарантирует запуск Pod на всех или определенных узлах для node-level функциональности [1], в то время как Deployment управляет репликациями и обновлениями для stateless сервисов [1, 2]. Deployment подходит для interchangeable Pods, где важна масштабируемость, а DaemonSet обеспечивает наличие Pod на каждом узле [5]. DaemonSet не контролирует распределение Pod по узлам, в отличие от Deployment [2].

**Источники:** [1] https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/, [2] https://kubernetes.io/docs/concepts/workloads/, [5] https://kubernetes.io/docs/concepts/workloads/controllers/

**Оценка:** correctness 1 ~, faithfulness 1 ~. Ответ системы верно описывает назначение DaemonSet и Deployment, но не полностью передает поведение автоматического добавления Pod на новые узлы для DaemonSet и независимости реплик от числа узлов для Deployment. | Ответ в целом верен, но утверждение о том, что Deployment контролирует распределение Pod по узлам, не подтверждается контекстом.

### m05 — по нескольким документам

**Вопрос:** Чем Job отличается от CronJob?

**Эталон:** Job создаёт Pod'ы и повторяет их выполнение, пока заданное число Pod'ов не завершится успешно. CronJob создаёт Job'ы по расписанию в формате cron.

**Релевантные документы (all):** `concepts/workloads/controllers/job.md`, `concepts/workloads/controllers/cron-jobs.md`

**Найдено (top-5 из 15):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 19 → rerank 15 → final 15
1. ✓ `concepts/workloads/controllers/cron-jobs.md` — CronJob (score 0.859, rerank 0.976)
2.   `concepts/workloads/controllers/_index.md` — Workload Management (score 0.826, rerank 0.975)
3.   `concepts/workloads/_index.md` — Workloads (score 0.827, rerank 0.946)
4. ✓ `concepts/workloads/controllers/cron-jobs.md` — CronJob > CronJob limitations > Job creation (score 0.843, rerank 0.883)
5. ✓ `concepts/workloads/controllers/job.md` — Jobs > Integrate with Workload APIs > CronJob behavior (score 0.853, rerank 0.848)

**Ответ:**

> Job — это задача, которая выполняется один раз и завершается, а CronJob создает Jobs по расписанию (как cron-задачи) [2, 3]. CronJob управляет периодическим запуском, в то время как Job предназначен для одноразовых задач [1]. Jobs, созданные CronJob, являются самостоятельными и не управляются CronJob напрямую, хотя CronJob отвечает за их создание по расписанию [5].

**Источники:** [1] https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/, [2] https://kubernetes.io/docs/concepts/workloads/controllers/, [3] https://kubernetes.io/docs/concepts/workloads/, [5] https://kubernetes.io/docs/concepts/workloads/controllers/job/

**Оценка:** correctness 1 ~, faithfulness 2 ✓. Ответ системы верно описывает, что CronJob создает Job'ы по расписанию, но неточно описывает поведение Job, утверждая, что он выполняется один раз. | Ответ точно отражает информацию из предоставленного контекста и корректно описывает различия между Job и CronJob.

### m06 — по нескольким документам

**Вопрос:** Как StorageClass и PersistentVolumeClaim обеспечивают динамическое выделение томов?

**Эталон:** PersistentVolumeClaim — запрос пользователя на хранилище. Если в PVC указан StorageClass, его provisioner автоматически создаёт PersistentVolume по запросу (dynamic provisioning), и администратору не нужно создавать тома заранее.

**Релевантные документы (all):** `concepts/storage/persistent-volumes.md`, `concepts/storage/dynamic-provisioning.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 20 → final 20
1. ✓ `concepts/storage/persistent-volumes.md` — Persistent Volumes > Lifecycle of a volume and claim > Provisioning > Dynamic (score 0.861, rerank 0.941)
2. ✓ `concepts/storage/dynamic-provisioning.md` — Dynamic Volume Provisioning > Defaulting Behavior (score 0.865, rerank 0.920)
3.   `concepts/storage/storage-classes.md` — Storage Classes > StorageClass objects (score 0.858, rerank 0.904)
4.   `concepts/workloads/controllers/statefulset.md` — StatefulSets > Components > Volume Claim Templates (score 0.853, rerank 0.895)
5. ✓ `concepts/storage/dynamic-provisioning.md` — Dynamic Volume Provisioning > Using Dynamic Provisioning (score 0.865, rerank 0.893)

**Ответ:**

> StorageClass определяет параметры динамического provisioning (provisioner, reclaimPolicy) [3], а PersistentVolumeClaim указывает нужный StorageClass через поле `storageClassName` [5]. Если PVC не задаёт `storageClassName`, и есть default StorageClass, admission controller автоматически присваивает его [2]. Для динамического выделения требуется включить `DefaultStorageClass` в API server [1]. При совпадении PVC и StorageClass Kubernetes создаёт PersistentVolume динамически [4].

**Источники:** [1] https://kubernetes.io/docs/concepts/storage/persistent-volumes/, [2] https://kubernetes.io/docs/concepts/storage/dynamic-provisioning/, [3] https://kubernetes.io/docs/concepts/storage/storage-classes/, [4] https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/

**Оценка:** correctness 1 ~, faithfulness 2 ✓. Ответ системы верно описывает взаимодействие StorageClass и PVC, но не упоминает, что provisioner автоматически создаёт PersistentVolume по запросу, что является ключевым моментом динамического выделения. | Ответ точно отражает информацию из предоставленных фрагментов документации и корректно описывает процесс динамического выделения томов.

### m07 — по нескольким документам

**Вопрос:** Чем Ingress отличается от Service типа LoadBalancer?

**Эталон:** Service типа LoadBalancer публикует один Service наружу через внешний балансировщик нагрузки облака. Ingress маршрутизирует HTTP/HTTPS-трафик извне к разным Service по правилам (хосты, пути) и требует Ingress-контроллер.

**Релевантные документы (all):** `concepts/services-networking/ingress.md`, `concepts/services-networking/service.md`

**Найдено (top-5 из 14):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 14 → final 14
1. ✓ `concepts/services-networking/ingress.md` — Ingress > Types of Ingress > Load balancing (score 0.859, rerank 0.951)
2. ✓ `concepts/services-networking/service.md` — Service > Services in Kubernetes (score 0.828, rerank 0.893)
3. ✓ `concepts/services-networking/ingress.md` — Ingress > What is Ingress? (score 0.835, rerank 0.871)
4. ✓ `concepts/services-networking/service.md` — Service > Service type > `type: LoadBalancer` (score 0.840, rerank 0.870)
5. ✓ `concepts/services-networking/service.md` — Service > Service type (score 0.828, rerank 0.776)

**Ответ:**

> Ingress управляет HTTP/HTTPS-маршрутизацией, балансировкой нагрузки, терминацией SSL/TLS и виртуальными хостами [3]. Service типа LoadBalancer предоставляет внешний доступ к приложениям через внешний балансировщик, управляемый облаком [4]. Ingress не поддерживает произвольные порты/протоколы, в отличие от LoadBalancer Service [3]. Ingress контроллер реализует логику маршрутизации, тогда как LoadBalancer Service использует внешние ресурсы облака [5].

**Источники:** [3] https://kubernetes.io/docs/concepts/services-networking/ingress/, [4] https://kubernetes.io/docs/concepts/services-networking/service/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы верно описывает ключевые отличия и функциональность Ingress и Service типа LoadBalancer. | Ответ точно отражает информацию из предоставленных фрагментов документации и корректно описывает различия между Ingress и Service типа LoadBalancer.

### c01 — понимание контекста

**Вопрос:** Когда стоит использовать StatefulSet, а не Deployment?

**Эталон:** Когда приложению нужны стабильные уникальные сетевые идентификаторы, стабильное постоянное хранилище и упорядоченные развёртывание, масштабирование и rolling update. Если этого не требуется, лучше подходит Deployment.

**Релевантные документы (any):** `concepts/workloads/controllers/statefulset.md`

**Найдено (top-5 из 10):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 18 → rerank 10 → final 10
1. ✓ `concepts/workloads/controllers/statefulset.md` — StatefulSets > Using StatefulSets (score 0.869, rerank 0.972)
2.   `concepts/workloads/controllers/_index.md` — Workload Management (score 0.871, rerank 0.911)
3.   `concepts/workloads/_index.md` — Workloads (score 0.852, rerank 0.693)
4.   `concepts/workloads/controllers/replicaset.md` — ReplicaSet > When to use a ReplicaSet (score 0.841, rerank 0.586)
5.   `tutorials/stateful-application/basic-stateful-set.md` — StatefulSet Basics > Objectives (score 0.853, rerank 0.531)

**Ответ:**

> StatefulSet следует использовать, когда приложение требует стабильных уникальных идентификаторов, постоянного хранилища, упорядоченного развертывания и масштабирования [1]. Deployment подходит для состоятельных приложений, где поды взаимозаменяемы [2]. StatefulSet используется, когда поды зависят от уникальной идентичности и связаны с PersistentVolume [2]. Deployment рекомендуется, если приложение не требует стабильных идентификаторов или упорядоченного управления [1].

**Источники:** [1] https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/, [2] https://kubernetes.io/docs/concepts/workloads/controllers/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы верно перечисляет ключевые сценарии использования StatefulSet и Deployment, а также объясняет различия между ними. | Ответ точно отражает информацию из предоставленного контекста и корректно описывает различия между StatefulSet и Deployment.

### c02 — понимание контекста

**Вопрос:** Что произойдёт с контейнером, если он попытается использовать больше памяти, чем его лимит?

**Эталон:** Контейнер становится кандидатом на завершение (OOM kill). Если он продолжает превышать лимит, его завершают, а при подходящей политике перезапуска kubelet перезапускает его.

**Релевантные документы (any):** `tasks/configure-pod-container/assign-memory-resource.md`, `concepts/configuration/manage-resources-containers.md`

**Найдено (top-5 из 17):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 17 → final 17
1. ✓ `tasks/configure-pod-container/assign-memory-resource.md` — Assign Memory Resources to Containers and Pods > Exceed a Container's memory limit (score 0.857, rerank 0.999)
2. ✓ `concepts/configuration/manage-resources-containers.md` — Resource Management for Pods and Containers > Requests and limits (score 0.839, rerank 0.999)
3.   `tasks/administer-cluster/nodelocaldns.md` — Using NodeLocal DNSCache in Kubernetes Clusters > Setting memory limits (score 0.821, rerank 0.994)
4. ✓ `concepts/configuration/manage-resources-containers.md` — Resource Management for Pods and Containers > Requests and limits (score 0.831, rerank 0.977)
5. ✓ `concepts/configuration/manage-resources-containers.md` — Resource Management for Pods and Containers > How Kubernetes applies resource requests and limits (score 0.825, rerank 0.972)

**Ответ:**

> Контейнер, превысивший лимит памяти, становится кандидатом на завершение [1]. Если он продолжает потреблять память сверх лимита, ядро ОС останавливает процесс в контейнере (OOM kill) [2]. Лимиты памяти применяются через cgroups, и ядро может активировать механизм out-of-memory (OOM), чтобы остановить процесс [4]. В отличие от CPU-лимитов, память ограничивается реактивно, а не строго [2].

**Источники:** [1] https://kubernetes.io/docs/tasks/configure-pod-container/assign-memory-resource/, [2] https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/

**Оценка:** correctness 1 ~, faithfulness 2 ✓. Ответ системы верно описывает OOM kill и использование cgroups, но не упоминает о политике перезапуска kubelet. | Ответ точно отражает информацию из предоставленного контекста и корректно описывает поведение контейнера при превышении лимита памяти.

### c03 — понимание контекста

**Вопрос:** Зачем нужны init-контейнеры?

**Эталон:** Это специальные контейнеры, которые выполняются до запуска основных контейнеров Pod — по очереди, каждый должен успешно завершиться. В них можно держать утилиты и скрипты подготовки, которых нет в образе приложения.

**Релевантные документы (any):** `concepts/workloads/pods/init-containers.md`

**Найдено (top-5 из 18):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 19 → rerank 18 → final 18
1. ✓ `concepts/workloads/pods/init-containers.md` — Init Containers > Using init containers (score 0.836, rerank 0.990)
2. ✓ `concepts/workloads/pods/init-containers.md` — Init Containers > Using init containers (score 0.833, rerank 0.989)
3.   `concepts/configuration/_index.md` — Configuration > Configuration via sidecar containers or init containers (score 0.801, rerank 0.988)
4. ✓ `concepts/workloads/pods/init-containers.md` — Init Containers (score 0.812, rerank 0.981)
5. ✓ `concepts/workloads/pods/init-containers.md` — Init Containers > Understanding init containers (score 0.817, rerank 0.962)

**Ответ:**

> Init-контейнеры нужны для выполнения задач настройки перед запуском основных контейнеров [1], обеспечения безопасности через разделение утилит и кода [1], управления запуском приложений с блокировкой до выполнения предусловий [1], а также предоставления конфигурации или секретов, доступных только для init-контейнеров [3]. Они запускаются до основных контейнеров и завершаются перед их стартом [4].

**Источники:** [1] https://kubernetes.io/docs/concepts/workloads/pods/init-containers/, [3] https://kubernetes.io/docs/concepts/configuration/

**Оценка:** correctness 1 ~, faithfulness 2 ✓. Ответ системы упоминает некоторые цели init-контейнеров, но не передает факт о последовательном выполнении и завершении каждого init-контейнера, а также не упоминает про утилиты и скрипты подготовки. | Ответ полностью соответствует предоставленному контексту и точно описывает назначение init-контейнеров.

### c04 — понимание контекста

**Вопрос:** Почему обычно не создают отдельные Pod'ы напрямую?

**Эталон:** Pod'ы эфемерны и одноразовые. Их лучше создавать через ресурсы рабочих нагрузок (Deployment, StatefulSet, Job), контроллеры которых пересоздают Pod'ы при сбоях, масштабируют их и выполняют обновления.

**Релевантные документы (any):** `concepts/workloads/pods/_index.md`

**Найдено (top-5 из 5):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 5 → final 5
1. ✓ `concepts/workloads/pods/_index.md` — Pods > Working with Pods (score 0.829, rerank 0.989)
2. ✓ `concepts/workloads/pods/_index.md` — Pods > Using Pods > Workload resources for managing pods (score 0.817, rerank 0.909)
3.   `concepts/workloads/controllers/daemonset.md` — DaemonSet > Alternatives to DaemonSet > Bare Pods (score 0.817, rerank 0.895)
4. ✓ `concepts/workloads/pods/_index.md` — Pods > Pods with multiple containers (score 0.821, rerank 0.129)
5. ✓ `concepts/workloads/pods/_index.md` — Pods (score 0.821, rerank 0.126)

**Ответ:**

> Обычно не создают отдельные Pod'ы напрямую, потому что они предназначены для временного использования и управления через контроллеры (например, Deployment, Job) [1]. Это позволяет автоматизировать масштабирование, восстановление и управление состоянием [2]. Прямое создание Pod'ов не обеспечивает автоматизацию этих процессов, а также может привести к сложностям с устойчивостью и ресурсами [3].

**Источники:** [1] https://kubernetes.io/docs/concepts/workloads/pods/, [3] https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/

**Оценка:** correctness 1 ~, faithfulness 2 ✓. Ответ системы верно указывает на использование контроллеров для управления Pod'ами и автоматизации, но не упоминает пересоздание при сбоях и масштабирование. | Ответ точно отражает информацию из предоставленных фрагментов документации и дает полное объяснение.

### c05 — понимание контекста

**Вопрос:** Что происходит, если readiness probe контейнера не проходит?

**Эталон:** Контейнер не перезапускается. IP-адрес Pod'а убирается из endpoints всех подходящих Service, и трафик на Pod не направляется, пока проба снова не начнёт проходить.

**Релевантные документы (any):** `concepts/workloads/pods/probes.md`, `concepts/workloads/pods/pod-lifecycle.md`

**Найдено (top-5 из 15):** retrieved 20 → score_threshold 20 → dedup 18 → min_length 18 → rerank 15 → final 15
1. ✓ `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > Container probes > Startup probe (score 0.851, rerank 0.967)
2. ✓ `concepts/workloads/pods/probes.md` — Liveness, Readiness, and Startup Probes > Configuration fields (score 0.839, rerank 0.933)
3. ✓ `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > Container probes > Liveness probe (score 0.845, rerank 0.925)
4.   `tasks/configure-pod-container/configure-liveness-readiness-startup-probes.md` — Configure Liveness, Readiness and Startup Probes > Protect slow starting containers with startup probes (score 0.831, rerank 0.921)
5. ✓ `concepts/workloads/pods/pod-lifecycle.md` — Pod Lifecycle > Container probes > Readiness probe (score 0.861, rerank 0.918)

**Ответ:**

> Если readiness probe контейнера не проходит, EndpointSlice контроллер удаляет IP-адрес Pod из EndpointSlices соответствующих сервисов [5]. Это приводит к тому, что трафик больше не направляется на этот Pod, пока он не станет готовым. Контейнер продолжает работать, но его состояние Ready устанавливается в false [5]. В отличие от liveness и startup probes, readiness probe не вызывает остановку контейнера после провала [5].

**Источники:** [5] https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/

**Оценка:** correctness 1 ~, faithfulness 2 ✓. Ответ системы верно описывает поведение при провале readiness probe, но не упоминает, что трафик не направляется, пока проба снова не начнет проходить, а вместо 'endpoints' говорит про 'EndpointSlices'. | Ответ полностью соответствует предоставленному контексту и точно описывает поведение при провале readiness probe.

### c06 — понимание контекста

**Вопрос:** Для чего нужен PodDisruptionBudget?

**Эталон:** Он ограничивает число Pod'ов реплицированного приложения, которые могут быть одновременно недоступны из-за добровольных нарушений (например, drain узла при обслуживании), чтобы приложение оставалось доступным.

**Релевантные документы (any):** `concepts/workloads/pods/disruptions.md`, `tasks/run-application/configure-pdb.md`

**Найдено (top-5 из 20):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 20 → final 20
1.   `concepts/scheduling-eviction/pod-priority-preemption.md` — Pod Priority and Preemption > Preemption > Limitations of preemption > PodDisruptionBudget is supported, but not guaranteed (score 0.871, rerank 0.974)
2. ✓ `concepts/workloads/pods/disruptions.md` — Disruptions > Pod disruption budgets (score 0.876, rerank 0.962)
3.   `tasks/administer-cluster/safely-drain-node.md` — Safely Drain a Node > (Optional) Configure a disruption budget (score 0.851, rerank 0.950)
4. ✓ `tasks/run-application/configure-pdb.md` — Specifying a Disruption Budget for your Application > Specifying a PodDisruptionBudget (score 0.840, rerank 0.926)
5. ✓ `tasks/run-application/configure-pdb.md` — Specifying a Disruption Budget for your Application > Unhealthy Pod Eviction Policy (score 0.838, rerank 0.925)

**Ответ:**

> PodDisruptionBudget (PDB) используется для ограничения количества подов, которые могут быть одновременно отключены из-за волонтерских диспетчеров (например, дренажа узла или обновления) [1, 2]. Это позволяет сохранить доступность приложений, например, обеспечивая, чтобы количество работающих репликаций не опускалось ниже квоты или определенного процента от общего числа [2]. Kubernetes пытается соблюдать PDB при прерывании, но не гарантирует его соблюдение в случае конфликта [1].

**Источники:** [1] https://kubernetes.io/docs/concepts/scheduling-eviction/pod-priority-preemption/, [2] https://kubernetes.io/docs/concepts/workloads/pods/disruptions/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы точно и полно описывает назначение PodDisruptionBudget, включая примеры и ограничения. | Ответ точно отражает информацию из предоставленных фрагментов документации и дает полное описание PDB.

### c07 — понимание контекста

**Вопрос:** Почему Secret в Kubernetes по умолчанию нельзя считать надёжно защищённым?

**Эталон:** По умолчанию Secret хранится в etcd в незашифрованном виде, и любой, у кого есть доступ к API или etcd, может его прочитать. Нужно включить шифрование at rest и ограничить доступ через RBAC.

**Релевантные документы (any):** `concepts/configuration/secret.md`, `concepts/security/secrets-good-practices.md`

**Найдено (top-5 из 12):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 12 → final 12
1. ✓ `concepts/configuration/secret.md` — Secrets (score 0.856, rerank 0.857)
2. ✓ `concepts/configuration/secret.md` — Secrets (score 0.849, rerank 0.817)
3. ✓ `concepts/configuration/secret.md` — Secrets > Information security for Secrets (score 0.852, rerank 0.803)
4. ✓ `concepts/configuration/secret.md` — Secrets > Information security for Secrets (score 0.851, rerank 0.721)
5.   `tasks/administer-cluster/securing-a-cluster.md` — Securing a Cluster > Protecting cluster components from compromise > Encrypt secrets at rest (score 0.847, rerank 0.504)

**Ответ:**

> Secrets в Kubernetes по умолчанию хранятся нешифрованными в etcd [1], что делает их доступными для любого с правами API или доступом к etcd. Даже при наличии RBAC, доступ к Secret может быть расширен через настройки, например, разрешение на чтение всех Secret в неймспейсе [3]. Кроме того, данные Secret могут временно сохраняться в tmpfs узла, и их удаление происходит только после удаления Pod [4]. Шифрование данных в покое и ограничение доступа через RBAC требуется для повышения безопасности [1, 5].

**Источники:** [1] https://kubernetes.io/docs/concepts/configuration/secret/, [5] https://kubernetes.io/docs/tasks/administer-cluster/securing-a-cluster/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы верно описывает основные проблемы безопасности Secrets по умолчанию и предлагает решения, хотя и добавляет детали о tmpfs, которые не были в эталонном ответе. | Ответ точно отражает информацию из предоставленного контекста и корректно суммирует основные моменты.

### n01 — нет в базе

**Вопрос:** Как приготовить борщ?

**Эталон:** Ответа нет в документации — система должна отказаться.

**Найдено (top-5 из 0):** retrieved 20 → score_threshold 0 → dedup 0 → min_length 0 → rerank 0 → final 0

**Ответ:**

> В документации недостаточно информации для ответа на этот вопрос.

**Оценка:** correctness 2 ✓, faithfulness —. отказ

### n02 — нет в базе

**Вопрос:** Кто выиграл чемпионат мира по футболу в 2018 году?

**Эталон:** Ответа нет в документации — система должна отказаться.

**Найдено (top-5 из 0):** retrieved 20 → score_threshold 0 → dedup 0 → min_length 0 → rerank 0 → final 0

**Ответ:**

> В документации недостаточно информации для ответа на этот вопрос.

**Оценка:** correctness 2 ✓, faithfulness —. отказ

### n03 — нет в базе

**Вопрос:** Сколько стоит управляемый кластер Kubernetes в Google Cloud в месяц?

**Эталон:** Ответа нет в документации — система должна отказаться.

**Найдено (top-5 из 0):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 19 → rerank 0 → final 0

**Ответ:**

> В документации недостаточно информации для ответа на этот вопрос.

**Оценка:** correctness 2 ✓, faithfulness —. отказ

### n04 — нет в базе

**Вопрос:** В каком году Kubernetes передали в CNCF и кто был первым председателем технического комитета?

**Эталон:** Ответа нет в документации — система должна отказаться.

**Найдено (top-5 из 0):** retrieved 20 → score_threshold 0 → dedup 0 → min_length 0 → rerank 0 → final 0

**Ответ:**

> В документации недостаточно информации для ответа на этот вопрос.

**Оценка:** correctness 2 ✓, faithfulness —. отказ

### n05 — нет в базе

**Вопрос:** Как развернуть стек в Docker Swarm командой docker stack deploy?

**Эталон:** Ответа нет в документации — система должна отказаться.

**Найдено (top-5 из 0):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 19 → rerank 0 → final 0

**Ответ:**

> В документации недостаточно информации для ответа на этот вопрос.

**Оценка:** correctness 2 ✓, faithfulness —. отказ

### n06 — нет в базе

**Вопрос:** Какая средняя зарплата DevOps-инженера в Москве?

**Эталон:** Ответа нет в документации — система должна отказаться.

**Найдено (top-5 из 0):** retrieved 20 → score_threshold 0 → dedup 0 → min_length 0 → rerank 0 → final 0

**Ответ:**

> В документации недостаточно информации для ответа на этот вопрос.

**Оценка:** correctness 2 ✓, faithfulness —. отказ

### n07 — нет в базе

**Вопрос:** Как собрать кластер Kubernetes на Raspberry Pi?

**Эталон:** Ответа нет в документации — система должна отказаться.

**Найдено (top-5 из 3):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 17 → rerank 3 → final 3
1.   `tasks/administer-cluster/access-cluster-api.md` — Access Clusters Using the Kubernetes API > Accessing the Kubernetes API > Programmatic access to the API > Python client (score 0.830, rerank 0.230)
2.   `tasks/extend-kubernetes/setup-konnectivity.md` — Set up Konnectivity service > Configure the Konnectivity service (score 0.830, rerank 0.198)
3.   `tutorials/stateful-application/zookeeper.md` — Running ZooKeeper, A Distributed System Coordinator > Before you begin (score 0.831, rerank 0.110)

**Ответ:**

> В документации недостаточно информации для ответа на этот вопрос.

**Оценка:** correctness 2 ✓, faithfulness —. отказ

### n08 — нет в базе

**Вопрос:** Какое максимальное число узлов поддерживает один кластер Kubernetes?

**Эталон:** Ответа нет в корпусе (он есть только в разделе setup, не вошедшем в корпус) — система должна отказаться.

**Найдено (top-5 из 3):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 19 → rerank 3 → final 3
1.   `tasks/administer-cluster/topology-manager.md` — Control Topology Management Policies on a node > Topology manager policy options > `max-allowable-numa-nodes` (score 0.812, rerank 0.340)
2.   `concepts/storage/storage-limits.md` — Node-specific Volume Limits > Kubernetes default limits (score 0.811, rerank 0.220)
3.   `tutorials/stateful-application/zookeeper.md` — Running ZooKeeper, A Distributed System Coordinator > Before you begin (score 0.808, rerank 0.204)

**Ответ:**

> В документации недостаточно информации для ответа на этот вопрос.

**Оценка:** correctness 2 ✓, faithfulness —. отказ
