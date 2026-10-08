# Прогон `E8/gemma3_12b`

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
- `llm`: gemma3-12b
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
| все вопросы | 0.787 | 0.984 | 0.988 | 40 |
| с ответом | 0.734 | 0.984 | 0.988 | 32 |
| фактологические | 0.950 | 1.000 | 1.000 | 10 |
| поиск конкретики | 0.812 | 1.000 | 1.000 | 8 |
| по нескольким документам | 0.572 | 1.000 | 1.000 | 7 |
| понимание контекста | 0.500 | 0.928 | 0.946 | 7 |
| нет в базе | 1.000 | — | — | 8 |

Correctness для вопросов без ответа: 1 — система отказалась. Faithfulness считается только для ответов, а не отказов.
Claim support — доля утверждений ответа, для которых судья нашёл цитату в контексте (как faithfulness в RAGAS).

Средняя задержка: retrieval 0.3128 с, generation 2.3759 с

## По вопросам

| id | Тип | Hit@5 | RR | Отказ | Correctness | Faithfulness |
|---|---|--:|--:|:-:|:-:|:-:|
| f01 | фактологические | 1.000 | 1.000 | нет | 2 ✓ | 2 ✓ |
| f02 | фактологические | 1.000 | 1.000 | нет | 2 ✓ | 2 ✓ |
| f03 | фактологические | 1.000 | 1.000 | нет | 1 ~ | 2 ✓ |
| f04 | фактологические | 1.000 | 1.000 | нет | 2 ✓ | 2 ✓ |
| f05 | фактологические | 1.000 | 1.000 | нет | 2 ✓ | 2 ✓ |
| f06 | фактологические | 1.000 | 1.000 | нет | 2 ✓ | 2 ✓ |
| f07 | фактологические | 1.000 | 1.000 | нет | 2 ✓ | 2 ✓ |
| f08 | фактологические | 1.000 | 0.500 | нет | 2 ✓ | 2 ✓ |
| f09 | фактологические | 1.000 | 1.000 | нет | 2 ✓ | 2 ✓ |
| f10 | фактологические | 1.000 | 1.000 | нет | 2 ✓ | 2 ✓ |
| s01 | поиск конкретики | 1.000 | 1.000 | нет | 2 ✓ | 2 ✓ |
| s02 | поиск конкретики | 1.000 | 0.500 | нет | 1 ~ | 2 ✓ |
| s03 | поиск конкретики | 1.000 | 1.000 | нет | 2 ✓ | 2 ✓ |
| s04 | поиск конкретики | 1.000 | 1.000 | нет | 1 ~ | 2 ✓ |
| s05 | поиск конкретики | 0.000 | 0.000 | нет | 1 ~ | 2 ✓ |
| s06 | поиск конкретики | 1.000 | 1.000 | нет | 2 ✓ | 2 ✓ |
| s07 | поиск конкретики | 1.000 | 1.000 | нет | 2 ✓ | 2 ✓ |
| s08 | поиск конкретики | 1.000 | 1.000 | нет | 2 ✓ | 2 ✓ |
| m01 | по нескольким документам | 1.000 | 0.333 | нет | 1 ~ | 2 ✓ |
| m02 | по нескольким документам | 1.000 | 1.000 | нет | 1 ~ | 2 ✓ |
| m03 | по нескольким документам | 1.000 | 1.000 | нет | 2 ✓ | 2 ✓ |
| m04 | по нескольким документам | 1.000 | 1.000 | нет | 1 ~ | 2 ✓ |
| m05 | по нескольким документам | 1.000 | 1.000 | нет | 1 ~ | 2 ✓ |
| m06 | по нескольким документам | 1.000 | 1.000 | нет | 1 ~ | 2 ✓ |
| m07 | по нескольким документам | 1.000 | 1.000 | нет | 1 ~ | 2 ✓ |
| c01 | понимание контекста | 1.000 | 1.000 | нет | 1 ~ | 2 ✓ |
| c02 | понимание контекста | 1.000 | 1.000 | нет | 1 ~ | 2 ✓ |
| c03 | понимание контекста | 1.000 | 1.000 | нет | 1 ~ | 2 ✓ |
| c04 | понимание контекста | 1.000 | 1.000 | нет | 1 ~ | 2 ✓ |
| c05 | понимание контекста | 1.000 | 1.000 | нет | 1 ~ | 2 ✓ |
| c06 | понимание контекста | 1.000 | 0.500 | нет | 1 ~ | 1 ~ |
| c07 | понимание контекста | 1.000 | 1.000 | нет | 1 ~ | 2 ✓ |
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

> Pod — это наименьшая развертываемая единица вычислений в Kubernetes [1]. Он представляет собой группу из одного или нескольких контейнеров, имеющих общие ресурсы хранения и сети, а также спецификацию для запуска контейнеров [2]. Pod моделирует "логический хост", специфичный для приложения [1, 5].  Pod может содержать как контейнеры приложения, так и init-контейнеры для запуска при старте Pod, а также временные контейнеры для отладки [1].  В большинстве случаев Pod содержит один контейнер [3], но может содержать несколько тесно связанных контейнеров [3, 5].

**Источники:** [1] https://kubernetes.io/docs/concepts/workloads/pods/, [2] https://kubernetes.io/docs/tutorials/kubernetes-basics/explore/explore-intro/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы полностью передает ключевые факты об определении Pod, добавляя полезные детали о init-контейнерах и отладке. | Ответ точно отражает информацию из предоставленного контекста и дает полное описание Pod.

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

> Компонент control plane, хранящий все данные кластера, — это `etcd` [1]. Это распределенное хранилище пар ключ-значение, обеспечивающее согласованность и высокую доступность [1].

**Источники:** [1] https://kubernetes.io/docs/concepts/overview/components/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы полностью соответствует эталонному, перечисляя ключевые характеристики etcd. | Ответ точно соответствует информации, представленной в контексте, и не содержит выдуманных деталей.

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

> HTTP API kubelet обычно доступен на TCP порту 10250 на рабочих узлах кластера [1]. В некоторых случаях он может быть доступен на узлах плоскости управления, в зависимости от используемого дистрибутива Kubernetes [1]. Для неаутентифицированных запросов в режиме автономной работы kubelet может использовать порт 10255 [2].

**Источники:** [1] https://kubernetes.io/docs/concepts/security/api-server-bypass-risks/, [2] https://kubernetes.io/docs/tutorials/cluster-management/kubelet-standalone/

**Оценка:** correctness 1 ~, faithfulness 2 ✓. Ответ системы содержит правильный порт, но также упоминает дополнительные порты и сценарии, которые не были затронуты в эталонном ответе, что снижает оценку. | Ответ точно отражает информацию, представленную в предоставленных фрагментах документации.

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

> По умолчанию порты для Service типа NodePort выделяются из диапазона 30000-32767 [1]. Этот диапазон делится на две полосы: статическую (30000-30085) и динамическую (30086-32767) [2]. Динамическое назначение портов использует верхнюю полосу, а при её исчерпании может использовать нижнюю [2].

**Источники:** [1] https://kubernetes.io/docs/concepts/services-networking/service/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы полностью соответствует эталонному и даже предоставляет дополнительную информацию о разделении диапазона на статическую и динамическую части. | Ответ полностью соответствует контексту и точно описывает диапазон портов и его разделение.

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

> kube-scheduler — это компонент Kubernetes, который выбирает оптимальный узел для запуска новых или еще не запланированных Pod'ов [1, 2]. Он фильтрует узлы, чтобы найти подходящие (feasible) узлы, а затем оценивает их, выбирая узел с наивысшим рейтингом [3, 4].  В процессе выбора учитываются различные факторы, такие как требования к ресурсам, ограничения и спецификации affinity/anti-affinity [4].  После выбора, kube-scheduler уведомляет API server о своем решении в процессе, называемом Binding [1, 4].

**Источники:** [1] https://kubernetes.io/docs/concepts/scheduling-eviction/kube-scheduler/, [2] https://kubernetes.io/docs/concepts/scheduling-eviction/scheduler-perf-tuning/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы полностью описывает функциональность kube-scheduler, перечисляя ключевые этапы процесса планирования. | Ответ точно отражает информацию, представленную в предоставленных фрагментах документации.

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

> По умолчанию значение `restartPolicy` для Pod равно `Always` [1]. Это значение применяется к контейнерам приложения и обычным init контейнерам. Стоит отметить, что для stateful приложений не рекомендуется изменять это значение [2].

**Источники:** [1] https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/, [2] https://kubernetes.io/docs/tutorials/stateful-application/zookeeper/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы полностью соответствует эталонному и предоставляет дополнительную информацию о применении restartPolicy. | Ответ точно соответствует контексту и предоставляет корректную информацию о default restartPolicy.

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

> Данные, хранящиеся в ConfigMap, не могут превышать 1 MiB [1]. Если вам нужно хранить настройки, превышающие этот лимит, рассмотрите возможность использования тома или отдельного сервиса базы данных или файла [1].

**Источники:** [1] https://kubernetes.io/docs/concepts/configuration/configmap/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы точно указывает максимальный объём данных, который можно хранить в ConfigMap, и предлагает альтернативные решения для хранения больших объёмов данных. | Ответ точно отражает информацию, представленную в контексте, и не содержит никаких дополнительных утверждений.

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

> Namespace в Kubernetes предоставляют механизм для изоляции групп ресурсов в пределах одного кластера [1, 3]. Они позволяют разделить ресурсы кластера между несколькими пользователями [2]. Namespace обеспечивают область видимости для имен ресурсов, где имена должны быть уникальными внутри Namespace, но не между ними [2, 3].  Namespace помогают разным проектам, командам или клиентам совместно использовать кластер Kubernetes [4].  Использование Namespace является необязательным [4].

**Источники:** [1] https://kubernetes.io/docs/concepts/security/multi-tenancy/, [2] https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/, [4] https://kubernetes.io/docs/tasks/administer-cluster/namespaces/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы полностью передает ключевые факты из эталонного ответа и добавляет полезную информацию об использовании Namespace. | Ответ полностью соответствует контексту и точно отражает назначение Namespace в Kubernetes.

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

> Фаза `Pending` означает, что Pod был принят кластером Kubernetes, но один или несколько контейнеров еще не были настроены и готовы к запуску [1]. Это включает в себя время ожидания Pod, пока ему будет назначена нода, а также время, затраченное на скачивание образов контейнеров по сети [1]. Обычно это происходит из-за нехватки ресурсов, таких как CPU или Memory [3].

**Источники:** [1] https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/, [3] https://kubernetes.io/docs/tasks/debug/debug-application/debug-pods/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы полностью соответствует эталонному, включая причины возникновения фазы Pending. | Ответ точно отражает информацию из предоставленного контекста и дает краткое и точное объяснение фазы Pending.

### f10 — фактологические

**Вопрос:** Какой тип Service создаётся, если тип не указан явно?

**Эталон:** ClusterIP.

**Релевантные документы (any):** `concepts/services-networking/service.md`

**Найдено (top-5 из 3):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 3 → final 3
1. ✓ `concepts/services-networking/service.md` — Service > Service type (score 0.793, rerank 0.605)
2. ✓ `concepts/services-networking/service.md` — Service > Headless Services > Without selectors (score 0.795, rerank 0.201)
3.   `tutorials/kubernetes-basics/expose/expose-intro.md` — Using a Service to Expose Your App > Overview of Kubernetes Services (score 0.813, rerank 0.168)

**Ответ:**

> Если тип Service не указан явно, создается Service типа `ClusterIP` [1]. Этот тип делает Service доступным только изнутри кластера [1]. Для доступа к Service извне кластера можно использовать Ingress или Gateway [1].

**Источники:** [1] https://kubernetes.io/docs/concepts/services-networking/service/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы полностью соответствует эталонному и предоставляет дополнительную информацию о доступности ClusterIP Service. | Ответ точно соответствует контексту и предоставляет корректную информацию о типе Service по умолчанию.

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

> Желаемое число реплик задается в поле `.spec.replicas` манифеста Deployment [1]. По умолчанию оно равно 1. При ручном масштабировании Deployment, например, с помощью `kubectl scale`, при повторном применении манифеста, ручное масштабирование будет перезаписано [1]. Если HorizontalPodAutoscaler управляет масштабированием, поле `.spec.replicas` не следует устанавливать [1].

**Источники:** [1] https://kubernetes.io/docs/concepts/workloads/controllers/deployment/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы полностью соответствует эталонному и содержит дополнительную полезную информацию о поведении поля. | Все утверждения точно отражают информацию, представленную в предоставленном контексте.

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

> Существует несколько способов изменить число реплик Deployment с помощью `kubectl` [2, 3, 4].
> 
> *   Используйте команду `kubectl scale deployments/<имя-deployment> --replicas=<желаемое-число-реплик>` [2].
> *   Обновите поле `.spec.replicas` с помощью стратегического merge patch: `kubectl patch deployment <имя-deployment> -p '{"spec":{"replicas":<желаемое-число-реплик>}}'` [1].
> *   Используйте команду `kubectl edit deployment <имя-deployment>` для изменения поля `.spec.replicas` в редакторе [4].
> *   Можно использовать JSON patch с предварительным тестом [1].
> *   Также можно использовать флаг `--subresource=[subresource-name]` с командой `kubectl patch` [3].

**Источники:** [1] https://kubernetes.io/docs/tasks/run-application/scale-deployment/, [2] https://kubernetes.io/docs/tutorials/kubernetes-basics/scale/scale-intro/, [3] https://kubernetes.io/docs/tasks/manage-kubernetes-objects/update-api-object-kubectl-patch/

**Оценка:** correctness 1 ~, faithfulness 2 ✓. Ответ системы предоставляет несколько способов изменения числа реплик, но не приводит эталонную команду `kubectl scale` и пример ее использования. | Все утверждения в ответе подтверждены фрагментами документации.

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

> Чтобы откатить Deployment на предыдущую ревизию, используйте команду `kubectl rollout undo deployment/nginx-deployment` [1].  Для отката к конкретной ревизии, укажите её с помощью флага `--to-revision`, например `kubectl rollout undo deployment/nginx-deployment --to-revision=2` [1, 2].

**Источники:** [1] https://kubernetes.io/docs/concepts/workloads/controllers/deployment/, [2] https://kubernetes.io/docs/tasks/run-application/update-deployment-rolling/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы полностью соответствует эталонному, включая пример команды и описание флага. | Ответ точно соответствует информации, представленной в контексте, и предоставляет правильные команды.

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

> Для задания лимита памяти контейнера необходимо включить поле `resources.limits.memory` в манифесте контейнера [1]. Также, если контейнер не задает лимит памяти, он будет ограничен до значения по умолчанию для пространства имен [3].

**Источники:** [1] https://kubernetes.io/docs/tasks/configure-pod-container/assign-memory-resource/, [3] https://kubernetes.io/docs/tasks/administer-cluster/manage-resources/memory-default-namespace/

**Оценка:** correctness 1 ~, faithfulness 2 ✓. Ответ системы верно указывает на поле `resources.limits.memory`, но не упоминает минимальный запрос памяти `resources.requests.memory`. | Оба утверждения точно отражают информацию, представленную в предоставленных фрагментах документации.

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

> Поле `topologySpreadConstraints` в `spec.topologySpreadConstraints` позволяет ограничивать узлы, на которых может запускаться Pod, на основе топологии [1]. Также можно использовать `node affinity` и `node selector` в шаблоне Pod для управления размещением [4]. Администраторы могут использовать `PodNodeSelector` для принудительного применения селектора узлов [3].

**Источники:** [1] https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/, [3] https://kubernetes.io/docs/tasks/administer-cluster/securing-a-cluster/, [4] https://kubernetes.io/docs/concepts/workloads/controllers/job/

**Оценка:** correctness 1 ~, faithfulness 2 ✓. Ответ системы упоминает `nodeSelector`, но также включает другие, менее простые способы, и неверно называет поле `PodNodeSelector`. | Ответ точно соответствует контексту и перечисляет рекомендованные поля для ограничения узлов.

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

> Можно настроить три вида проб: Startup probe, Liveness probe и Readiness probe [1, 2]. Startup probe проверяет, запущена ли программа внутри контейнера [5]. Liveness probe определяет, жив ли контейнер [2]. Readiness probe указывает, готов ли контейнер принимать трафик [2].

**Источники:** [1] https://kubernetes.io/docs/concepts/workloads/pods/probes/, [2] https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы перечисляет все три типа probes и кратко описывает их назначение, что соответствует эталонному ответу. | Ответ точно соответствует контексту и перечисляет все три типа проб, а также кратко описывает их назначение.

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

> Чтобы посмотреть логи предыдущего (упавшего) экземпляра контейнера, используйте команду `kubectl logs ${POD_NAME} -c ${CONTAINER_NAME} --previous` [1]. Если у вас несколько контейнеров в поде, укажите имя контейнера с флагом `-c` [2].

**Источники:** [1] https://kubernetes.io/docs/tasks/debug/debug-application/debug-running-pod/, [2] https://kubernetes.io/docs/concepts/cluster-administration/logging/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы полностью соответствует эталонному и содержит важные уточнения. | Ответ точно соответствует контексту и предоставляет правильную команду.

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

> Параметр `maxUnavailable` определяет максимальное количество Pod'ов, которые могут быть недоступны во время обновления Deployment [1, 2]. Значение может быть абсолютным числом или процентом от желаемого количества Pod'ов [1, 2]. По умолчанию установлено значение 25% [1, 2].

**Источники:** [1] https://kubernetes.io/docs/concepts/workloads/controllers/deployment/, [2] https://kubernetes.io/docs/tasks/run-application/update-deployment-rolling/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы полностью соответствует эталонному и передает все ключевые факты. | Ответ точно отражает информацию из предоставленного контекста и не содержит выдуманных деталей.

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

> Deployment подходит для управления stateless приложениями, где Pods взаимозаменяемы [1, 2]. StatefulSet же предназначен для управления Pods, которым требуется уникальная идентификация и постоянное хранилище [2, 3]. StatefulSet обеспечивает упорядоченное развертывание и масштабирование, а также упорядоченные обновления [3]. Deployment обеспечивает декларативные обновления для Pods и ReplicaSets [4].

**Источники:** [1] https://kubernetes.io/docs/concepts/workloads/controllers/, [2] https://kubernetes.io/docs/concepts/workloads/, [3] https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/, [4] https://kubernetes.io/docs/concepts/workloads/controllers/deployment/

**Оценка:** correctness 1 ~, faithfulness 2 ✓. Ответ системы верно указывает на stateless-приложения для Deployment и уникальную идентификацию/хранилище для StatefulSet, но не упоминает сетевой идентификатор и неточно описывает упорядоченные операции StatefulSet. | Ответ точно отражает информацию из предоставленных фрагментов документации и корректно описывает различия между Deployment и StatefulSet.

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

> ConfigMap и Secret похожи, но Secret предназначены для хранения конфиденциальных данных, таких как пароли, токены или ключи [1, 2]. ConfigMap хранят данные конфигурации в виде пар ключ-значение и предназначены для работы со строками, не содержащими конфиденциальную информацию [3]. ConfigMap не обеспечивает секретность или шифрование, поэтому для конфиденциальных данных следует использовать Secret [4]. Kubernetes применяет дополнительные меры защиты для Secret [5].

**Источники:** [1] https://kubernetes.io/docs/concepts/configuration/secret/, [2] https://kubernetes.io/docs/concepts/configuration/, [3] https://kubernetes.io/docs/tasks/configure-pod-container/configure-pod-configmap/, [4] https://kubernetes.io/docs/concepts/configuration/configmap/

**Оценка:** correctness 1 ~, faithfulness 2 ✓. Ответ системы верно описывает основные различия между ConfigMap и Secret, но не упоминает про небольшой объем данных, предназначенный для Secret. | Ответ точно отражает информацию из предоставленного контекста и корректно описывает различия между ConfigMap и Secret.

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

> Deployment управляет ReplicaSet и обеспечивает декларативные обновления Pod и ReplicaSet [3]. Deployment создает ReplicaSet для запуска желаемых Pod [4], и при обновлении Deployment создается новый ReplicaSet, а старые ReplicaSet постепенно масштабируются до 0 [4].  Рекомендуется использовать Deployment вместо прямого использования ReplicaSet, если не требуется пользовательская оркестровка обновлений или обновления вообще [2]. ReplicaSet в основном используются Deployment [1, 5].

**Источники:** [1] https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/, [3] https://kubernetes.io/docs/concepts/workloads/controllers/deployment/, [5] https://kubernetes.io/docs/concepts/workloads/controllers/replicationcontroller/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы верно описывает взаимосвязь между Deployment и ReplicaSet, а также подчеркивает преимущества использования Deployment. | Ответ точно отражает информацию из предоставленного контекста и правильно описывает взаимосвязь между Deployment и ReplicaSet.

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

> DaemonSet похож на Deployment тем, что оба создают Pods [1]. Однако, Deployment подходит для управления stateless приложениями, где важны масштабирование и обновления [2, 5]. DaemonSet используется, когда необходимо, чтобы копия Pod всегда работала на всех или определенных хостах, обеспечивая node-level функциональность [1, 2]. Например, сетевые плагины часто используют DaemonSet [1].

**Источники:** [1] https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/, [2] https://kubernetes.io/docs/concepts/workloads/, [5] https://kubernetes.io/docs/concepts/workloads/controllers/

**Оценка:** correctness 1 ~, faithfulness 2 ✓. Ответ системы верно указывает на node-level функциональность DaemonSet и связь Deployment со stateless приложениями, но не упоминает ключевое отличие в количестве реплик и неточно описывает DaemonSet как запускающий Pod на *всех* узлах. | Ответ точно отражает информацию из предоставленного контекста и корректно описывает различия между DaemonSet и Deployment.

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

> Job представляет собой одноразовую задачу, в то время как CronJob повторяет выполнение задачи по расписанию [2, 3]. CronJob создает Jobs на основе повторяющегося расписания [1]. Job отвечает за управление Pod'ами, а CronJob отвечает только за создание Jobs, соответствующих его расписанию [4]. Jobs, созданные CronJob, являются автономными и не управляются Workload объектами [5].

**Источники:** [1] https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/, [2] https://kubernetes.io/docs/concepts/workloads/controllers/, [3] https://kubernetes.io/docs/concepts/workloads/, [5] https://kubernetes.io/docs/concepts/workloads/controllers/job/

**Оценка:** correctness 1 ~, faithfulness 2 ✓. Ответ системы верно указывает, что CronJob создает Jobs по расписанию, но неточно описывает поведение Job, не упоминая повторное выполнение Pod'ов до успешного завершения. | Ответ точно отражает информацию из предоставленных фрагментов документации.

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

> StorageClass содержит параметры, такие как `provisioner`, `parameters` и `reclaimPolicy`, которые используются при динамическом выделении PersistentVolume для PersistentVolumeClaim [3]. Пользователи запрашивают динамическое выделение, указывая имя StorageClass в поле `storageClassName` PersistentVolumeClaim [5].  Для этого кластер должен быть настроен на динамическое выделение, а API-сервер должен иметь включенный контроллер `DefaultStorageClass` [1, 2]. Администратор может также назначить StorageClass по умолчанию, чтобы он применялся к PVC без указания `storageClassName` [2, 3].

**Источники:** [1] https://kubernetes.io/docs/concepts/storage/persistent-volumes/, [2] https://kubernetes.io/docs/concepts/storage/dynamic-provisioning/, [3] https://kubernetes.io/docs/concepts/storage/storage-classes/

**Оценка:** correctness 1 ~, faithfulness 2 ✓. Ответ системы верно описывает роль StorageClass и PVC в динамическом выделении, но не упоминает, что provisioner автоматически создает PersistentVolume, что является ключевым моментом. | Ответ точно отражает информацию из предоставленных фрагментов документации и последовательно описывает процесс динамического выделения томов.

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

> Ingress предназначен для маршрутизации HTTP и HTTPS трафика к сервисам внутри кластера, консолидируя правила маршрутизации в одном ресурсе [3]. Service типа LoadBalancer предоставляет внешний балансировщик нагрузки для сервиса, и его создание происходит асинхронно [4]. Ingress не является типом Service, а действует как точка входа в кластер [2].  В то время как Service типа LoadBalancer может использоваться для экспозиции сервисов, отличных от HTTP и HTTPS [3], Ingress не предназначен для этого.

**Источники:** [2] https://kubernetes.io/docs/concepts/services-networking/service/, [3] https://kubernetes.io/docs/concepts/services-networking/ingress/

**Оценка:** correctness 1 ~, faithfulness 2 ✓. Ответ системы верно описывает некоторые аспекты отличий, но упускает важную информацию о необходимости Ingress-контроллера и неточно описывает возможности Service типа LoadBalancer. | Ответ точно отражает информацию из предоставленного контекста и корректно описывает различия между Ingress и Service типа LoadBalancer.

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

> StatefulSet стоит использовать, когда приложению требуются стабильные, уникальные сетевые идентификаторы, стабильное, постоянное хранилище, упорядоченное развертывание и масштабирование, а также упорядоченные автоматические обновления [1]. StatefulSet подходит для приложений, которым требуется связь между Pod и постоянным хранилищем, например, для связывания каждого Pod с PersistentVolume [2]. Если приложению не нужны стабильные идентификаторы или упорядоченное развертывание, удаление или масштабирование, лучше использовать Deployment или ReplicaSet [1].

**Источники:** [1] https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/, [2] https://kubernetes.io/docs/concepts/workloads/controllers/

**Оценка:** correctness 1 ~, faithfulness 2 ✓. Ответ системы верно перечисляет основные причины использования StatefulSet, но не упоминает, что Deployment подходит, когда эти требования отсутствуют, что является важной частью эталонного ответа. | Ответ точно отражает информацию из предоставленного контекста и корректно суммирует ключевые моменты.

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

> Если контейнер попытается использовать больше памяти, чем его лимит, ядро может его завершить [2]. Контейнер может использовать больше памяти, чем его лимит, но в этом случае он может быть завершен [2, 4]. Если контейнер превышает свой лимит памяти, он становится кандидатом на завершение [1]. Завершение контейнера происходит, когда ядро обнаруживает нехватку памяти [2].

**Источники:** [1] https://kubernetes.io/docs/tasks/configure-pod-container/assign-memory-resource/, [2] https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/

**Оценка:** correctness 1 ~, faithfulness 2 ✓. Ответ системы верно описывает OOM kill и завершение контейнера, но не упоминает о политике перезапуска kubelet. | Все утверждения точно отражают информацию, представленную в предоставленных фрагментах документации.

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

> Init-контейнеры нужны для выполнения утилит или пользовательского кода для настройки, которые отсутствуют в образе приложения [1, 4]. Они позволяют разделить роли сборщика и развертывающего образа приложения [1]. Init-контейнеры могут предоставлять конфигурацию к рабочей нагрузке [3]. Они также могут выполнять код, который иначе сделал бы образ приложения менее безопасным [1].

**Источники:** [1] https://kubernetes.io/docs/concepts/workloads/pods/init-containers/, [3] https://kubernetes.io/docs/concepts/configuration/

**Оценка:** correctness 1 ~, faithfulness 2 ✓. Ответ системы верно описывает назначение init-контейнеров, но не упоминает о последовательном выполнении и завершении каждого init-контейнера. | Ответ точно отражает информацию из предоставленного контекста и не содержит выдуманных утверждений.

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

> Обычно отдельные Pod'ы не создают напрямую, даже если это singleton Pod [1, 2]. Вместо этого рекомендуется использовать ресурсы workload, такие как Deployment или Job [2].  DaemonSet заменяет Pod'ы, которые были удалены или завершены, что делает создание отдельных Pod'ов нежелательным [3]. Pod'ы рассматриваются как относительно эфемерные и одноразовые сущности [1].

**Источники:** [1] https://kubernetes.io/docs/concepts/workloads/pods/, [3] https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/

**Оценка:** correctness 1 ~, faithfulness 2 ✓. Ответ системы верно указывает на эфемерность Pod'ов и рекомендует использовать ресурсы workload, но не упоминает о пересоздании и масштабировании. | Ответ точно отражает информацию из предоставленного контекста и дает полное объяснение.

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

> Если readiness probe контейнера не проходит, kubelet продолжает выполнять контейнер и продолжает выполнять проверки. При этом kubelet устанавливает состояние `Ready` Pod в `false` [2]. Это означает, что Pod исключается из EndpointSlices всех соответствующих Services [5].

**Источники:** [2] https://kubernetes.io/docs/concepts/workloads/pods/probes/, [5] https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/

**Оценка:** correctness 1 ~, faithfulness 2 ✓. Ответ системы верно указывает на изменение состояния Pod в `false` и исключение из Services, но не упоминает о том, что контейнер не перезапускается и трафик не направляется. | Ответ точно отражает информацию из предоставленных фрагментов документации.

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

> PodDisruptionBudget (PDB) нужен для ограничения количества одновременно недоступных Pods приложения во время добровольных сбоев [2]. Он позволяет владельцам приложений ограничивать количество Pods, которые могут быть недоступны из-за добровольных сбоев [2]. PDB может быть настроен для обеспечения кворума или для поддержания определенного процента реплик, обслуживающих нагрузку [2].  Для настройки PDB рекомендуется использовать `AlwaysAllow` Unhealthy Pod Eviction Policy [3]. PDB имеет три поля: селектор, `minAvailable` и `maxUnavailable` [4].

**Источники:** [2] https://kubernetes.io/docs/concepts/workloads/pods/disruptions/, [3] https://kubernetes.io/docs/tasks/administer-cluster/safely-drain-node/, [4] https://kubernetes.io/docs/tasks/run-application/configure-pdb/

**Оценка:** correctness 1 ~, faithfulness 1 ~. Ответ системы верно описывает назначение PDB и некоторые его аспекты, но не упоминает drain узла, что является важным контекстом. | Ответ в целом верен и опирается на контекст, но некоторые детали о полях PDB не были явно упомянуты в ответе.

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

> По умолчанию Kubernetes Secrets хранятся незашифрованными в хранилище данных API-сервера (etcd) [1]. Любой, кто имеет доступ к API или etcd, может получить или изменить Secret [1]. Также, любой, кто может создавать Pod в namespace, может получить доступ к Secrets в этом namespace [3]. Для безопасного использования Secrets необходимо предпринять дополнительные шаги, такие как включение шифрования данных в состоянии покоя [1].

**Источники:** [1] https://kubernetes.io/docs/concepts/configuration/secret/

**Оценка:** correctness 1 ~, faithfulness 2 ✓. Ответ системы верно описывает хранение Secret в etcd и необходимость шифрования, но не упоминает про RBAC. | Ответ точно отражает информацию из предоставленного контекста и дает краткое объяснение, почему Secrets по умолчанию не безопасны.

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
