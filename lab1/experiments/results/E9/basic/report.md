# Прогон `E9/basic`

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
- `llm`: qwen3-8b
- `prompt`: basic
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

- Отказ на вопросы без ответа (верно): **75%**
- Ложный отказ на вопросы с ответом: **0%**
- Источники ответа содержат релевантный документ: **97%**
- Вызовов LLM: 34 из 40

## Оценка судьи (0..1)

| Группа | Correctness | Faithfulness | Claim support | N |
|---|--:|--:|--:|--:|
| все вопросы | 0.762 | 0.941 | 0.979 | 40 |
| с ответом | 0.766 | 0.938 | 0.978 | 32 |
| фактологические | 0.850 | 0.950 | 0.980 | 10 |
| поиск конкретики | 0.875 | 0.938 | 0.969 | 8 |
| по нескольким документам | 0.572 | 0.928 | 0.982 | 7 |
| понимание контекста | 0.714 | 0.928 | 0.982 | 7 |
| нет в базе | 0.750 | 1.000 | 1.000 | 8 |

Correctness для вопросов без ответа: 1 — система отказалась. Faithfulness считается только для ответов, а не отказов.
Claim support — доля утверждений ответа, для которых судья нашёл цитату в контексте (как faithfulness в RAGAS).

Средняя задержка: retrieval 0.2453 с, generation 3.9761 с

## По вопросам

| id | Тип | Hit@5 | RR | Отказ | Correctness | Faithfulness |
|---|---|--:|--:|:-:|:-:|:-:|
| f01 | фактологические | 1.000 | 1.000 | нет | 1 ~ | 2 ✓ |
| f02 | фактологические | 1.000 | 1.000 | нет | 2 ✓ | 2 ✓ |
| f03 | фактологические | 1.000 | 1.000 | нет | 2 ✓ | 2 ✓ |
| f04 | фактологические | 1.000 | 1.000 | нет | 2 ✓ | 2 ✓ |
| f05 | фактологические | 1.000 | 1.000 | нет | 2 ✓ | 2 ✓ |
| f06 | фактологические | 1.000 | 1.000 | нет | 2 ✓ | 2 ✓ |
| f07 | фактологические | 1.000 | 1.000 | нет | 2 ✓ | 2 ✓ |
| f08 | фактологические | 1.000 | 0.500 | нет | 1 ~ | 2 ✓ |
| f09 | фактологические | 1.000 | 1.000 | нет | 1 ~ | 1 ~ |
| f10 | фактологические | 1.000 | 1.000 | нет | 2 ✓ | 2 ✓ |
| s01 | поиск конкретики | 1.000 | 1.000 | нет | 2 ✓ | 2 ✓ |
| s02 | поиск конкретики | 1.000 | 0.500 | нет | 1 ~ | 2 ✓ |
| s03 | поиск конкретики | 1.000 | 1.000 | нет | 2 ✓ | 2 ✓ |
| s04 | поиск конкретики | 1.000 | 1.000 | нет | 1 ~ | 2 ✓ |
| s05 | поиск конкретики | 0.000 | 0.000 | нет | 2 ✓ | 1 ~ |
| s06 | поиск конкретики | 1.000 | 1.000 | нет | 2 ✓ | 2 ✓ |
| s07 | поиск конкретики | 1.000 | 1.000 | нет | 2 ✓ | 2 ✓ |
| s08 | поиск конкретики | 1.000 | 1.000 | нет | 2 ✓ | 2 ✓ |
| m01 | по нескольким документам | 1.000 | 0.333 | нет | 1 ~ | 2 ✓ |
| m02 | по нескольким документам | 1.000 | 1.000 | нет | 1 ~ | 2 ✓ |
| m03 | по нескольким документам | 1.000 | 1.000 | нет | 1 ~ | 2 ✓ |
| m04 | по нескольким документам | 1.000 | 1.000 | нет | 1 ~ | 2 ✓ |
| m05 | по нескольким документам | 1.000 | 1.000 | нет | 1 ~ | 2 ✓ |
| m06 | по нескольким документам | 1.000 | 1.000 | нет | 2 ✓ | 1 ~ |
| m07 | по нескольким документам | 1.000 | 1.000 | нет | 1 ~ | 2 ✓ |
| c01 | понимание контекста | 1.000 | 1.000 | нет | 2 ✓ | 2 ✓ |
| c02 | понимание контекста | 1.000 | 1.000 | нет | 1 ~ | 2 ✓ |
| c03 | понимание контекста | 1.000 | 1.000 | нет | 1 ~ | 1 ~ |
| c04 | понимание контекста | 1.000 | 1.000 | нет | 2 ✓ | 2 ✓ |
| c05 | понимание контекста | 1.000 | 1.000 | нет | 1 ~ | 2 ✓ |
| c06 | понимание контекста | 1.000 | 0.500 | нет | 2 ✓ | 2 ✓ |
| c07 | понимание контекста | 1.000 | 1.000 | нет | 1 ~ | 2 ✓ |
| n01 | нет в базе | — | — | да | 2 ✓ | — |
| n02 | нет в базе | — | — | да | 2 ✓ | — |
| n03 | нет в базе | — | — | да | 2 ✓ | — |
| n04 | нет в базе | — | — | да | 2 ✓ | — |
| n05 | нет в базе | — | — | да | 2 ✓ | — |
| n06 | нет в базе | — | — | да | 2 ✓ | — |
| n07 | нет в базе | — | — | нет | 0 ✗ | 2 ✓ |
| n08 | нет в базе | — | — | нет | 0 ✗ | 2 ✓ |

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

> **Pod** — это наименьшая развертываемая и управляемая единица вычислений в Kubernetes. Он представляет собой группу одного или более контейнеров, которые выполняются в общем контексте с общим сетевым и хранилищем ресурсами. 
> 
> Основные характеристики Pod:
> 
> - **Контейнеры**: Pod может содержать один или несколько контейнеров. В большинстве случаев используется модель "один контейнер на Pod", но также возможны случаи, когда в Podе находятся несколько тесно связанных контейнеров, которые работают вместе.
> - **Общие ресурсы**: Все контейнеры в Podе делят сетевой адрес, объемы хранения (Volumes) и другие ресурсы.
> - **Сетевая изоляция**: Каждый Pod имеет уникальный IP-адрес, и контейнеры внутри него делят сетевое пространство.
> - **Расположение и расписание**: Контейнеры в Podе всегда размещаются и распределяются вместе на одном узле (Node) кластера.
> - **Управление**: Kubernetes управляет Podами, а не отдельными контейнерами. При создании Deployment Kubernetes создает Podы, которые содержат контейнеры приложения.
> 
> Pod — это абстракция, которая моделирует "логический хост" для приложения и обеспечивает удобное управление и развертывание приложений в кластере Kubernetes.

**Источники:** [1] https://kubernetes.io/docs/concepts/workloads/pods/, [2] https://kubernetes.io/docs/tutorials/kubernetes-basics/explore/explore-intro/

**Оценка:** correctness 1 ~, faithfulness 2 ✓. Ответ системы верно описывает основные характеристики Pod, но не упоминает спецификацию запуска, что является важной частью определения. | Ответ точно отражает информацию из предоставленных фрагментов документации и дает исчерпывающее описание Pod.

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

> Компонент control plane, который хранит все данные кластера, — это **etcd**. Это распределённый ключ-значение хранилище, обеспечивающее согласованность и высокую доступность данных для всех компонентов API-сервера.

**Источники:** [1] https://kubernetes.io/docs/concepts/overview/components/, [2] https://kubernetes.io/docs/tutorials/kubernetes-basics/create-cluster/cluster-intro/, [3] https://kubernetes.io/docs/concepts/security/multi-tenancy/, [4] https://kubernetes.io/docs/tasks/administer-cluster/kubeadm/kubeadm-reconfigure/, [5] https://kubernetes.io/docs/concepts/architecture/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы полностью соответствует эталонному, перечисляя все ключевые факты. | Ответ точно соответствует информации, представленной в контексте, и не содержит выдуманных деталей.

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

> Обычно HTTP API kubelet на рабочих узлах использует порт **10250**.

**Источники:** [1] https://kubernetes.io/docs/concepts/security/api-server-bypass-risks/, [2] https://kubernetes.io/docs/tutorials/cluster-management/kubelet-standalone/, [3] https://kubernetes.io/docs/concepts/architecture/control-plane-node-communication/, [4] https://kubernetes.io/docs/concepts/security/controlling-access/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы полностью соответствует эталонному ответу и содержит правильный порт. | Ответ точно соответствует информации, представленной в контексте.

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

> По умолчанию порты для Service типа `NodePort` выделяются из диапазона **30000-32767**.

**Источники:** [1] https://kubernetes.io/docs/concepts/services-networking/service/, [4] https://kubernetes.io/docs/tasks/access-application-cluster/create-external-load-balancer/, [5] https://kubernetes.io/docs/tutorials/services/source-ip/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы полностью соответствует эталонному и точно указывает диапазон портов для Service типа NodePort. | Ответ точно соответствует информации, представленной во фрагменте [1].

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

> Kube-scheduler — это компонент Kubernetes, который отвечает за распределение новых или несвязанных (unscheduled) Pod'ов на узлы (nodes) кластера. Он выполняет следующие основные задачи:
> 
> 1. **Фильтрация узлов**:  
>    Kube-scheduler проверяет, какие узлы подходят для запуска Pod'а, учитывая такие факторы, как доступные ресурсы, требования Pod'а, аффинность и анти-аффинность, а также другие ограничения. Узлы, которые соответствуют требованиям Pod'а, называются *feasible nodes* (подходящими узлами).
> 
> 2. **Оценка узлов**:  
>    После фильтрации kube-scheduler оценивает каждый подходящий узл, чтобы определить, на каком из них Pod будет наиболее оптимально запущен. Оценка основывается на настраиваемых правилах, которые могут учитывать такие факторы, как локальность данных, интерференция между работами и другие.
> 
> 3. **Привязка Pod'а к узлу**:  
>    После оценки kube-scheduler выбирает узел с самой высокой оценкой и привязывает (binding) Pod к этому узлу. Этот процесс называется *binding*.
> 
> 4. **Учет пользовательских настроек**:  
>    Пользователь может указать конкретный узел для Pod'а при его создании, но это редко используется и применяется только в особых случаях.
> 
> 5. **Мониторинг и метрики**:  
>    Kube-scheduler также предоставляет метрики, которые помогают анализировать использование ресурсов, планировать емкость и выявлять проблемы с распределением.
> 
> Таким образом, kube-scheduler обеспечивает эффективное и оптимальное распределение Pod'ов по узлам кластера, учитывая различные требования и ограничения.

**Источники:** [1] https://kubernetes.io/docs/concepts/scheduling-eviction/kube-scheduler/, [2] https://kubernetes.io/docs/concepts/scheduling-eviction/scheduler-perf-tuning/, [5] https://kubernetes.io/docs/concepts/cluster-administration/system-metrics/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы полностью описывает функциональность kube-scheduler, включая фильтрацию, оценку и привязку Pod'ов к узлам. | Ответ точно отражает информацию из предоставленного контекста и предоставляет исчерпывающее описание функций kube-scheduler.

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

> По умолчанию значение `restartPolicy` у Pod равно `Always`.

**Источники:** [1] https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/, [2] https://kubernetes.io/docs/tutorials/stateful-application/zookeeper/, [5] https://kubernetes.io/docs/concepts/workloads/pods/init-containers/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы полностью соответствует эталонному и точно передает информацию о значении restartPolicy по умолчанию. | Ответ точно соответствует информации, представленной в контексте [1].

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

> Максимальный объём данных, который можно хранить в одном ConfigMap, составляет **1 МБ (мегабайт)**. Если вам нужно хранить данные, превышающие этот лимит, рекомендуется использовать другие способы, такие как монтирование тома или использование отдельной базы данных или файлового сервиса.

**Источники:** [1] https://kubernetes.io/docs/concepts/configuration/configmap/, [3] https://kubernetes.io/docs/tutorials/configuration/configure-redis-using-configmap/, [4] https://kubernetes.io/docs/concepts/storage/volumes/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы точно указывает максимальный размер ConfigMap как 1 МБ и предлагает альтернативные решения для хранения больших объемов данных. | Ответ точно соответствует информации, представленной в контексте, и не содержит никаких дополнительных или противоречивых утверждений.

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

> В Kubernetes **Namespaces** нужны для **изоляции групп ресурсов** внутри одного кластера и обеспечения **логической разделенности** между разными пользователями, командами или проектами. Основные цели и функции Namespaces:
> 
> 1. **Изоляция ресурсов**:  
>    Namespaces позволяют разделять ресурсы (например, Pods, Services, Deployments) на логические группы. Имена ресурсов должны быть уникальными внутри Namespaces, но могут повторяться в разных Namespaces.
> 
> 2. **Управление доступом и политиками**:  
>    Многие политики безопасности, такие как **RBAC (Role-Based Access Control)** и **Network Policies**, применяются на уровне Namespaces. Это позволяет ограничивать доступ к ресурсам и управлять правами пользователей и сервисных аккаунтов.
> 
> 3. **Разделение ресурсов между пользователями**:  
>    Namespaces помогают распределять ресурсы кластера (например, CPU, память) между разными пользователями или командами через **Resource Quotas**.
> 
> 4. **Упрощение управления в многопользовательских средах**:  
>    В кластерах с большим количеством пользователей Namespaces позволяют организовать работу по командам или проектам, изолируя их друг от друга и упрощая администрирование.
> 
> 5. **Поддержка многотенантности**:  
>    Namespaces позволяют разным "аренз" (например, разным командам или клиентам) использовать один и тот же кластер, обеспечивая изоляцию и управление доступом.
> 
> **Примечание**:  
> - Использование `default` Namespace в производственных кластерах не рекомендуется. Лучше создавать отдельные Namespaces для каждого проекта или команды.
> - Namespaces **не подходят** для разделения разных версий одного и того же приложения — для этого лучше использовать **labels** внутри одного Namespace.

**Источники:** [1] https://kubernetes.io/docs/concepts/security/multi-tenancy/, [2] https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/, [4] https://kubernetes.io/docs/tasks/administer-cluster/namespaces/

**Оценка:** correctness 1 ~, faithfulness 2 ✓. Ответ системы верно описывает изоляцию ресурсов и уникальность имен в пределах namespace, но неявно подразумевает, что имена уникальны между namespace, что не совсем верно. | Ответ полностью соответствует контексту и точно описывает назначение и функции Namespaces в Kubernetes.

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

> Фаза `Pending` у Pod означает, что Pod был принят кластером Kubernetes, но ещё не может быть назначен узлу для запуска. Это может происходить по разным причинам, например, из-за недостатка ресурсов (CPU, памяти), недоступности узлов или настройки параметров, таких как `hostPort`. В это время Pod может ждать расписания или загрузки образов контейнеров с сети.

**Источники:** [1] https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/, [3] https://kubernetes.io/docs/tasks/debug/debug-application/debug-pods/

**Оценка:** correctness 1 ~, faithfulness 1 ~. Ответ системы верно указывает на принятие Pod кластером и ожидание планирования, но не упоминает, что контейнеры не готовы к запуску, а лишь подразумевает это. | Ответ в целом верен и опирается на контекст, но утверждение о недоступности узлов как причине Pending не подтверждается напрямую.

### f10 — фактологические

**Вопрос:** Какой тип Service создаётся, если тип не указан явно?

**Эталон:** ClusterIP.

**Релевантные документы (any):** `concepts/services-networking/service.md`

**Найдено (top-5 из 3):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 20 → rerank 3 → final 3
1. ✓ `concepts/services-networking/service.md` — Service > Service type (score 0.793, rerank 0.605)
2. ✓ `concepts/services-networking/service.md` — Service > Headless Services > Without selectors (score 0.795, rerank 0.201)
3.   `tutorials/kubernetes-basics/expose/expose-intro.md` — Using a Service to Expose Your App > Overview of Kubernetes Services (score 0.813, rerank 0.168)

**Ответ:**

> Если тип Service не указан явно, создаётся Service типа `ClusterIP`. Это значение по умолчанию, и оно позволяет Service быть доступным только внутри кластера. Для доступа к Service извне кластера можно использовать Ingress или Gateway.

**Источники:** [1] https://kubernetes.io/docs/concepts/services-networking/service/, [3] https://kubernetes.io/docs/tutorials/kubernetes-basics/expose/expose-intro/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы полностью соответствует эталонному и предоставляет дополнительную полезную информацию. | Ответ точно соответствует контексту и предоставляет корректную информацию о типе Service по умолчанию.

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

> Желаемое число реплик в манифесте Deployment задаёт поле `.spec.replicas`. Это поле определяет количество Pod'ов, которые должны быть запущены и доступны для работы. Если это поле не указано, оно по умолчанию устанавливается в значение 1.

**Источники:** [1] https://kubernetes.io/docs/concepts/workloads/controllers/deployment/, [3] https://kubernetes.io/docs/tutorials/kubernetes-basics/scale/scale-intro/, [5] https://kubernetes.io/docs/tutorials/cluster-management/admission-policies/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы полностью соответствует эталонному и добавляет полезную информацию о значении по умолчанию. | Ответ точно соответствует контексту и предоставляет корректную информацию о поле `.spec.replicas`.

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

> Чтобы изменить число реплик Deployment, можно использовать следующие команды `kubectl`:
> 
> 1. **Через `kubectl scale`**:
>    ```shell
>    kubectl scale deployments/<имя_deployment> --replicas=<нужное_число>
>    ```
> 
> 2. **Через `kubectl patch` (стратегический merge patch)**:
>    ```shell
>    kubectl patch deployment <имя_deployment> -p '{"spec":{"replicas":<нужное_число>}}'
>    ```
> 
> 3. **Через `kubectl patch` с использованием JSON-патча и проверкой (test)**:
>    ```shell
>    kubectl patch deployment <имя_deployment> --type=json -p='[
>      {"op": "test", "path": "/spec/replicas", "value": <текущее_число>},
>      {"op": "replace", "path": "/spec/replicas", "value": <нужное_число>}
>    ]'
>    ```
> 
> 4. **Через редактирование Deployment (kubectl edit)**:
>    ```shell
>    kubectl edit deployment <имя_deployment>
>    ```
>    После открытия редактора измените значение `.spec.replicas` и сохраните изменения.
> 
> Все эти команды позволяют изменить количество реплик Deployment в зависимости от ваших потребностей и сценариев.

**Источники:** [1] https://kubernetes.io/docs/tasks/run-application/scale-deployment/, [2] https://kubernetes.io/docs/tutorials/kubernetes-basics/scale/scale-intro/, [3] https://kubernetes.io/docs/tasks/manage-kubernetes-objects/update-api-object-kubectl-patch/, [5] https://kubernetes.io/docs/concepts/workloads/controllers/deployment/

**Оценка:** correctness 1 ~, faithfulness 2 ✓. Ответ системы предоставляет несколько способов изменения количества реплик, но не приводит конкретный пример, как в эталонном ответе. | Ответ полностью соответствует предоставленному контексту и предоставляет все упомянутые способы изменения числа реплик Deployment.

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

> Чтобы откатить Deployment на предыдущую ревизию, можно использовать следующую команду:
> 
> ```shell
> kubectl rollout undo deployment/nginx-deployment --to-revision=2
> ```
> 
> Эта команда откатит Deployment `nginx-deployment` на ревизию 2. Если нужно откатить на конкретную ревизию, обязательно укажите параметр `--to-revision` с номером нужной ревизии.

**Источники:** [1] https://kubernetes.io/docs/concepts/workloads/controllers/deployment/, [2] https://kubernetes.io/docs/tasks/run-application/update-deployment-rolling/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы полностью соответствует эталонному, включая пример команды и объяснение параметра --to-revision. | Ответ точно соответствует предоставленному контексту и предоставляет корректную информацию о команде отката и связанных аспектах.

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

> В манифесте контейнера поле, которое задаёт лимит памяти, это `resources.limits.memory`.

**Источники:** [1] https://kubernetes.io/docs/tasks/configure-pod-container/assign-memory-resource/, [2] https://kubernetes.io/docs/tasks/configure-pod-container/assign-pod-level-resources/, [3] https://kubernetes.io/docs/tasks/administer-cluster/manage-resources/memory-default-namespace/, [4] https://kubernetes.io/docs/tasks/administer-cluster/manage-resources/memory-constraint-namespace/

**Оценка:** correctness 1 ~, faithfulness 2 ✓. Ответ системы верно указывает поле для лимита памяти, но не упоминает минимальный запрос памяти. | Ответ точно соответствует информации, представленной в контексте.

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

> Самый простой рекомендуемый способ ограничить узлы, на которых может запускаться Pod, по меткам узлов — это поле `nodeSelector`. 
> 
> Это поле позволяет указать, какие узлы могут запускать Pod, основываясь на метках, присвоенных узлам. Оно является частью `spec` Pod и используется вместе с метками узлов для обеспечения правильного размещения Pod на нужных узлах.

**Источники:** [1] https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/, [2] https://kubernetes.io/docs/concepts/security/security-checklist/, [3] https://kubernetes.io/docs/tasks/administer-cluster/securing-a-cluster/, [4] https://kubernetes.io/docs/concepts/workloads/controllers/job/, [5] https://kubernetes.io/docs/concepts/security/pod-security-standards/

**Оценка:** correctness 2 ✓, faithfulness 1 ~. Ответ системы полностью соответствует эталонному и предоставляет дополнительную информацию о `nodeSelector`. | Ответ утверждает, что `nodeSelector` — самый простой способ, но в контексте нет такого утверждения; однако, он правильно описывает функциональность `nodeSelector`.

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

> Для контейнера можно настроить три вида проб (probes):
> 
> 1. **Startup probe** (проба запуска) — используется для проверки, завершил ли приложение в контейнере инициализацию.
> 2. **Liveness probe** (проба живости) — используется для определения, работает ли контейнер корректно. Если проба не проходит, Kubernetes перезапускает контейнер.
> 3. **Readiness probe** (проба готовности) — используется для определения, готов ли контейнер принимать трафик. Если проба не проходит, Kubernetes перестаёт направлять трафик на этот контейнер.

**Источники:** [1] https://kubernetes.io/docs/concepts/workloads/pods/probes/, [2] https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/, [3] https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы полностью перечисляет все три типа probes и дает краткое описание каждого из них. | Ответ точно отражает информацию из предоставленного контекста и корректно описывает назначение каждого типа probes.

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

> Чтобы посмотреть логи предыдущего (упавшего) экземпляра контейнера, используйте следующую команду:
> 
> ```shell
> kubectl logs ${POD_NAME} -c ${CONTAINER_NAME} --previous
> ```

**Источники:** [1] https://kubernetes.io/docs/tasks/debug/debug-application/debug-running-pod/, [2] https://kubernetes.io/docs/concepts/cluster-administration/logging/, [3] https://kubernetes.io/docs/tutorials/stateful-application/zookeeper/, [4] https://kubernetes.io/docs/tasks/inject-data-application/downward-api-volume-expose-pod-information/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы полностью соответствует эталонному, хотя и использует переменные окружения вместо прямого указания имени пода и контейнера. | Ответ точно соответствует информации, представленной во фрагменте 1 документации.

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

> Параметр `maxUnavailable` задаёт, сколько Pod'ов может быть недоступно во время обновления Deployment.

**Источники:** [1] https://kubernetes.io/docs/concepts/workloads/controllers/deployment/, [2] https://kubernetes.io/docs/tasks/run-application/update-deployment-rolling/, [3] https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/, [5] https://kubernetes.io/docs/tutorials/kubernetes-basics/update/update-intro/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы верно идентифицирует параметр `maxUnavailable` и его назначение. | Ответ точно соответствует контексту и правильно идентифицирует параметр `maxUnavailable`.

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

> Deployment и StatefulSet — это два разных типа workload в Kubernetes, которые предназначены для управления Pods, но они различаются по своим характеристикам и использованию.
> 
> **Основные различия:**
> 
> 1. **Состояние приложения:**
>    - **Deployment** используется для управления **состоятельными (stateless)** приложениями. Pods в Deployment могут быть заменены друг на друга, и их порядок не имеет значения.
>    - **StatefulSet** используется для управления **приложениями с состоянием (stateful)**. Каждый Pod в StatefulSet имеет уникальную идентичность и зависит от стабильного сетевого идентификатора, а также от стабильного хранилища.
> 
> 2. **Сетевые идентификаторы:**
>    - **Deployment** не гарантирует стабильных сетевых идентификаторов для Pods.
>    - **StatefulSet** предоставляет **стабильные, уникальные сетевые идентификаторы** для каждого Pod.
> 
> 3. **Хранилище:**
>    - **Deployment** не поддерживает привязку к PersistentVolume. Если требуется, каждый Pod может использовать отдельное PersistentVolume, но это не гарантируется.
>    - **StatefulSet** позволяет привязать каждый Pod к **PersistentVolume**, что обеспечивает **стабильное и.persistent хранилище**.
> 
> 4. **Порядок развертывания и масштабирования:**
>    - **Deployment** разворачивает и масштабирует Pods **последовательно**, но порядок не имеет значения.
>    - **StatefulSet** гарантирует **упорядоченное развертывание, масштабирование и обновление**. Pods создаются и удаляются в определенном порядке (от 0 до N-1 и обратно).
> 
> 5. **Обновления:**
>    - **Deployment** поддерживает **автоматические обновления** и ротацию.
>    - **StatefulSet** также поддерживает **автоматические обновления**, но с учетом порядка и зависимости между Pods.
> 
> 6. **Терминация Pods:**
>    - **Deployment** не требует особого порядка при завершении Pods.
>    - **StatefulSet** гарантирует, что **все последующие Pods** завершатся перед завершением текущего Pod.
> 
> **Вывод:**  
> Deployment подходит для **состоятельных (stateless)** приложений, где Pods могут быть заменены друг на друга. StatefulSet используется для **приложений с состоянием (stateful)**, где каждый Pod имеет уникальную идентичность и зависит от стабильного хранилища и сетевых идентификаторов.

**Источники:** [1] https://kubernetes.io/docs/concepts/workloads/controllers/, [2] https://kubernetes.io/docs/concepts/workloads/, [3] https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/, [4] https://kubernetes.io/docs/concepts/workloads/controllers/deployment/

**Оценка:** correctness 1 ~, faithfulness 2 ✓. Ответ системы верно описывает основные различия между Deployment и StatefulSet, но не упоминает декларативные обновления для Deployment. | Ответ точно отражает различия между Deployment и StatefulSet, основываясь на предоставленном контексте.

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

> ConfigMap и Secret — это два типа объектов в Kubernetes, которые используются для хранения конфигурационных данных, но они отличаются по целям и способам использования:
> 
> 1. **Назначение**:
>    - **ConfigMap** предназначен для хранения **нестандартных строковых данных**, которые **не содержат конфиденциальной информации**. Например, это могут быть настройки приложения, пути к файлам, параметры конфигурации и т.д.
>    - **Secret** используется для хранения **конфиденциальной информации**, такой как пароли, токены, сертификаты и ключи. Secret обеспечивает дополнительную защиту данных.
> 
> 2. **Безопасность**:
>    - ConfigMap **не обеспечивает секретности или шифрования**. Если данные требуют защиты, их следует хранить в Secret.
>    - Secret в Kubernetes **имеет дополнительные меры безопасности**, такие как ограничение доступа к данным, защита от записи в неvolatile-хранилище и другие меры, чтобы минимизировать риски утечки информации.
> 
> 3. **Использование в Pod**:
>    - Оба объекта могут использоваться в Pod для предоставления конфигурационных данных. Однако Secret используется для передачи **конфиденциальных данных**, а ConfigMap — для **общих настроек**.
>    - При использовании в Pod данные из ConfigMap могут быть доступны как файлы в томе, а данные из Secret — как переменные окружения или файлы, но с дополнительной защитой.
> 
> 4. **Формат данных**:
>    - ConfigMap может содержать **простые строки** (например, через `--from-literal`) или **сложные структуры**, такие как JSON или YAML (через `--from-file`).
>    - Secret также может содержать строки или файлы, но данные в нем **рассматриваются как конфиденциальные** и не должны быть доступны всем.
> 
> **Вывод**: ConfigMap используется для хранения **нестандартных строковых данных**, а Secret — для **конфиденциальной информации**. Secret обеспечивает дополнительную защиту данных, что делает его более подходящим для хранения чувствительной информации.

**Источники:** [1] https://kubernetes.io/docs/concepts/configuration/secret/, [2] https://kubernetes.io/docs/concepts/configuration/, [3] https://kubernetes.io/docs/tasks/configure-pod-container/configure-pod-configmap/, [4] https://kubernetes.io/docs/concepts/configuration/configmap/

**Оценка:** correctness 1 ~, faithfulness 2 ✓. Ответ системы верно описывает основные отличия ConfigMap и Secret, хотя и немного расширяет их описание. | Ответ точно отражает информацию из предоставленного контекста и корректно описывает различия между ConfigMap и Secret.

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

> Deployment и ReplicaSet — это связанные объекты в Kubernetes, где Deployment управляет ReplicaSet. 
> 
> Deployment предоставляет механизм для декларативного управления ReplicaSet и подключенными к ним Pod'ами. Он обеспечивает контролируемую замену, обновление и масштабирование. При создании Deployment создаются соответствующие ReplicaSet, которые отвечают за запуск и управление конкретными Pod'ами.
> 
> ReplicaSet, в свою очередь, гарантирует, что определенное количество Pod'ов будет запущено и доступно в любое время. Однако, в большинстве случаев, вместо прямого управления ReplicaSet рекомендуется использовать Deployment, так как он упрощает управление и обеспечивает более гибкие возможности обновления и масштабирования.
> 
> Таким образом, Deployment — это более высокий уровень абстракции, который управляет ReplicaSet, а ReplicaSet — это механизм, который обеспечивает поддержку нужного количества Pod'ов.

**Источники:** [1] https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/, [3] https://kubernetes.io/docs/concepts/workloads/controllers/deployment/, [5] https://kubernetes.io/docs/concepts/workloads/controllers/replicationcontroller/

**Оценка:** correctness 1 ~, faithfulness 2 ✓. Ответ системы верно описывает связь между Deployment и ReplicaSet, но не упоминает конкретно про rolling update и откаты, что является важной частью функциональности Deployment. | Ответ точно отражает взаимосвязь между Deployment и ReplicaSet, как описано в предоставленных фрагментах документации.

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

> DaemonSet и Deployment — это два разных типа контроллеров в Kubernetes, предназначенные для управления Pods, но они решают разные задачи.
> 
> **Основные отличия:**
> 
> 1. **Цель использования:**
>    - **Deployment** используется для управления **безстатными** приложениями, где важна возможность масштабирования, обновления и замены отдельных Pods. Примеры: фронтенд-серверы, веб-серверы.
>    - **DaemonSet** используется для обеспечения того, чтобы **каждый узел** в кластере имел один и только один Pod, выполняющий определённую функцию (например, сетевой плагин, мониторинг). Это аналогично системным демонам в Unix-системах.
> 
> 2. **Распределение Pods:**
>    - **Deployment** создаёт определённое количество Pods (реплики), которые могут быть распределены по узлам кластера. Количество реплик можно масштабировать.
>    - **DaemonSet** гарантирует, что на каждом подходящем узле будет запущен один Pod. Если добавляется новый узел, Kubernetes автоматически запускает Pod для DaemonSet на этом узле.
> 
> 3. **Интерфейс управления:**
>    - **Deployment** позволяет управлять версиями приложения, выполнять обновления, откатывать изменения и т.д.
>    - **DaemonSet** не поддерживает обновления в таком же виде, как Deployment. Он фокусируется на том, чтобы гарантировать наличие Pods на всех узлах.
> 
> 4. **Состояние Pods:**
>    - **Deployment** подходит для **безстатных** сервисов, где Pods могут быть заменены друг на друга.
>    - **DaemonSet** используется для **узел-ориентированных** задач, где каждый Pod выполняет уникальную роль на своём узле.
> 
> **Примеры использования:**
> - **Deployment:** Веб-сервер, который можно масштабировать.
> - **DaemonSet:** Сетевой плагин, который должен работать на каждом узле кластера.
> 
> Таким образом, **Deployment** подходит для управления приложениями, где важна гибкость и масштабируемость, а **DaemonSet** — для обеспечения функциональности на уровне узлов.

**Источники:** [1] https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/, [2] https://kubernetes.io/docs/concepts/workloads/, [3] https://kubernetes.io/docs/concepts/workloads/controllers/deployment/, [4] https://kubernetes.io/docs/concepts/extend-kubernetes/compute-storage-net/device-plugins/, [5] https://kubernetes.io/docs/concepts/workloads/controllers/

**Оценка:** correctness 1 ~, faithfulness 2 ✓. Ответ системы верно описывает DaemonSet и Deployment, но неточно передает факт о Deployment - не указано, что количество реплик задается независимо от количества узлов. | Ответ точно отражает различия между DaemonSet и Deployment, основываясь на предоставленном контексте.

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

> **Job** и **CronJob** — это два разных типа ресурсов в Kubernetes, которые используются для управления задачами, но они отличаются по своей функциональности:
> 
> 1. **Job**:
>    - Используется для запуска задач, которые должны выполняться **однократно** и завершаться.
>    - Он гарантирует, что задание будет выполнено, даже если оно завершится с ошибкой или прервано.
>    - Job не повторяется автоматически. Он запускается вручную или через другой ресурс (например, CronJob).
> 
> 2. **CronJob**:
>    - Используется для запуска задач **по расписанию**, например, ежедневно, еженедельно или в определённое время.
>    - Он работает аналогично строке в crontab (расписании cron) на Unix-системах.
>    - CronJob автоматически запускает Job в соответствии с заданным расписанием.
>    - Он может создавать несколько Job одновременно, если расписание было пропущено из-за проблем с контроллером или других обстоятельств.
> 
> **Вывод**:  
> **Job** — это задача, которая выполняется один раз, а **CronJob** — это расписываемый запуск задач, который может запускать несколько Job в соответствии с заданным расписанием.

**Источники:** [1] https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/, [2] https://kubernetes.io/docs/concepts/workloads/controllers/, [3] https://kubernetes.io/docs/concepts/workloads/, [5] https://kubernetes.io/docs/concepts/workloads/controllers/job/

**Оценка:** correctness 1 ~, faithfulness 2 ✓. Ответ системы верно описывает назначение CronJob и Job, но неверно описывает поведение Job (не повторяет Pod'ы). | Ответ точно отражает различия между Job и CronJob, основываясь на предоставленной документации.

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

> StorageClass и PersistentVolumeClaim обеспечивают динамическое выделение томов в Kubernetes следующим образом:
> 
> 1. **StorageClass** — это объект, который определяет параметры динамического выделения тома. Он содержит такие поля, как `provisioner`, `parameters` и `reclaimPolicy`. Эти поля указывают, каким образом и с какими параметрами должен быть создан PersistentVolume (PV) при необходимости. Также StorageClass может быть отмечен как **default**, чтобы автоматически использоваться, если в PersistentVolumeClaim (PVC) не указано имя StorageClass.
> 
> 2. **PersistentVolumeClaim (PVC)** — это заявка на использование хранилища. Пользователь создаёт PVC и указывает в нём `storageClassName`, который должен совпадать с именем уже существующего StorageClass. Если StorageClass настроен на динамическое выделение, Kubernetes автоматически создаёт соответствующий PersistentVolume (PV) для удовлетворения запроса в PVC.
> 
> 3. **Динамическое выделение** происходит, если:
>    - В PVC указано имя StorageClass, который настроен на динамическое выделение.
>    - Или, если StorageClass отмечен как **default**, и в PVC не указано имя StorageClass. В этом случае Kubernetes автоматически назначает default StorageClass.
> 
> 4. **Процесс динамического выделения**:
>    - Пользователь создаёт PVC с указанием `storageClassName`.
>    - Kubernetes проверяет, существует ли StorageClass с таким именем и настроен ли он на динамическое выделение.
>    - Если всё верно, Kubernetes запускает процесс создания PV через provisioner, указанный в StorageClass.
>    - После создания PV, он привязывается к PVC, и ресурс становится доступен для использования приложением.
> 
> Таким образом, StorageClass задаёт правила и параметры динамического выделения, а PVC запрашивает хранилище, используя эти правила.

**Источники:** [1] https://kubernetes.io/docs/concepts/storage/persistent-volumes/, [2] https://kubernetes.io/docs/concepts/storage/dynamic-provisioning/, [3] https://kubernetes.io/docs/concepts/storage/storage-classes/, [4] https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/

**Оценка:** correctness 2 ✓, faithfulness 1 ~. Ответ системы полностью описывает процесс динамического выделения томов, используя StorageClass и PersistentVolumeClaim, и верно передает ключевые факты. | Ответ в целом верен и опирается на контекст, но утверждение о привязке PV к PVC и доступности для приложения не содержится в предоставленных фрагментах.

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

> Ingress и Service типа LoadBalancer — это два разных механизма в Kubernetes, которые решают разные задачи, хотя оба могут использоваться для распределения трафика к приложениям внутри кластера.
> 
> ### Основные различия:
> 
> 1. **Цель и функции:**
>    - **Ingress** — это ресурс, который управляет HTTP/HTTPS-маршрутизацией. Он позволяет объединить несколько сервисов в один точку входа и настроить правила маршрутизации (например, по имени домена или пути URL). Ingress может выполнять такие задачи, как терминирование TLS/SSL, виртуальное хостинг и балансировка нагрузки.
>    - **Service типа LoadBalancer** — это способ вынести сервис за пределы кластера, используя внешний балансировщик нагрузки. Он предоставляет внешний IP-адрес, через который можно достучаться до сервиса, но не управляет маршрутизацией HTTP/HTTPS.
> 
> 2. **Типы протоколов:**
>    - Ingress работает только с HTTP/HTTPS. Он не поддерживает другие протоколы.
>    - Service типа LoadBalancer может работать с любыми протоколами (например, TCP, UDP), если это поддерживается обработчиком балансировщика.
> 
> 3. **Конфигурация и управление:**
>    - Ingress требует **Ingress controller**, который реализует логику маршрутизации. Например, NGINX, Traefik, HAProxy и т.д. Ingress controller отвечает за реализацию правил Ingress.
>    - Service типа LoadBalancer не требует отдельного контроллера. Он просто предоставляет внешний IP-адрес, и трафик направляется на соответствующие Pods через внутреннюю балансировку.
> 
> 4. **Балансировка нагрузки:**
>    - Ingress может использовать балансировку нагрузки, но она зависит от конкретного Ingress controller. Некоторые контроллеры поддерживают продвинутые функции, такие как динамические веса, сессии и т.д.
>    - Service типа LoadBalancer использует внешний балансировщик, предоставляемый облаком (например, AWS ELB, GCP Load Balancer), и его настройки зависят от провайдера.
> 
> 5. **Доступ к внешним ресурсам:**
>    - Ingress может быть настроен для маршрутизации трафика к внешним URL (например, через TLS-сертификаты), но это не его основная функция.
>    - Service типа LoadBalancer предоставляет внешний IP-адрес, который можно использовать для доступа к сервису извне.
> 
> ### Итог:
> - **Ingress** — это способ маршрутизации HTTP/HTTPS-трафика к сервисам внутри кластера.
> - **Service типа LoadBalancer** — это способ вынести сервис за пределы кластера с помощью внешнего балансировщика.
> 
> Оба механизма могут использоваться вместе: например, Ingress может быть настроен на использование внешнего балансировщика (через Service типа LoadBalancer) для распределения трафика.

**Источники:** [1] https://kubernetes.io/docs/concepts/services-networking/ingress/, [2] https://kubernetes.io/docs/concepts/services-networking/service/

**Оценка:** correctness 1 ~, faithfulness 2 ✓. Ответ системы верно описывает основные различия между Ingress и Service типа LoadBalancer, но не упоминает, что Ingress работает на уровне HTTP/HTTPS, а Service типа LoadBalancer может работать с любыми протоколами. | Ответ точно отражает различия между Ingress и Service типа LoadBalancer, основываясь на предоставленном контексте.

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

> StatefulSet стоит использовать вместо Deployment в следующих случаях:
> 
> 1. **Когда приложение требует стабильных, уникальных идентификаторов сетевых интерфейсов**. Каждый Pod в StatefulSet имеет уникальное имя и стабильный IP-адрес, что важно для приложений, которые зависят от идентификаторов.
> 
> 2. **Когда приложение требует стабильного, постоянного хранилища**. StatefulSet позволяет связать каждый Pod с отдельным PersistentVolume, что обеспечивает сохранение данных даже при перезапуске Pod.
> 
> 3. **Когда требуется упорядоченная и гладкая развертка, масштабирование и обновление**. StatefulSet обеспечивает упорядоченные операции, такие как масштабирование, обновление и удаление, что важно для распределенных систем и приложений с состоянием.
> 
> 4. **Когда приложение является распределенным и требует управления состоянием**. Например, базы данных, распределенные системы или приложения, которые хранят данные в нескольких Pod'ах.
> 
> В противном случае, если приложение не требует стабильного идентификатора, постоянного хранилища или упорядоченных операций, лучше использовать Deployment, так как он предназначен для управления состоятельными репликами.

**Источники:** [1] https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/, [2] https://kubernetes.io/docs/concepts/workloads/controllers/, [3] https://kubernetes.io/docs/concepts/workloads/, [4] https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/, [5] https://kubernetes.io/docs/tutorials/stateful-application/basic-stateful-set/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы полностью соответствует эталонному, перечисляя все ключевые факты и давая правильное заключение о выборе между StatefulSet и Deployment. | Ответ полностью соответствует контексту и точно отражает случаи использования StatefulSet по сравнению с Deployment.

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

> Если контейнер попытается использовать больше памяти, чем его лимит, то:
> 
> 1. **Контейнер может быть остановлен (OOMKilled)**: Если контейнер использует больше памяти, чем его лимит, ядро Linux активирует систему "out-of-memory" (OOM), которая может остановить контейнер. Это происходит, если система обнаружит нехватку памяти.
> 
> 2. **Контейнер может быть завершён без немедленного уничтожения**: В некоторых случаях контейнер может временно использовать больше памяти, чем его лимит, но не сразу быть уничтожен. Это зависит от того, какое давление на память существует на узле.
> 
> 3. **Контейнер может быть перезапущен**: Если контейнер был остановлен из-за превышения лимита памяти и он настроен на перезапуск (например, если он является частью Deployment или DaemonSet), Kubernetes может попытаться перезапустить его, как и в случае с другими сбоями.
> 
> 4. **Поведение зависит от настроек и версии ядра Linux**: В некоторых случаях, особенно при использовании cgroup v2, может применяться функция MemoryQoS, которая добавляет механизм торможения памяти и возможную резервацию памяти по уровням.
> 
> Таким образом, если контейнер попытается использовать больше памяти, чем его лимит, он может быть остановлен, но не обязательно сразу, и в зависимости от настроек системы может быть перезапущен.

**Источники:** [1] https://kubernetes.io/docs/tasks/configure-pod-container/assign-memory-resource/, [2] https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/, [3] https://kubernetes.io/docs/tasks/administer-cluster/nodelocaldns/

**Оценка:** correctness 1 ~, faithfulness 2 ✓. Ответ системы верно описывает OOM kill и возможность перезапуска, но не упоминает политику перезапуска и неточно описывает процесс завершения. | Ответ точно отражает информацию из предоставленных фрагментов документации и предоставляет полное описание возможных сценариев.

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

> Init-контейнеры нужны для выполнения задач инициализации перед запуском основных контейнеров в Pod. Они позволяют:
> 
> 1. **Выполнять подготовительные задачи**: Например, установку утилит (например, `sed`, `awk`, `python`) или выполнение скриптов настройки, которые не входят в образ основного приложения.
> 2. **Разделение ролей**: Разделить роли построителя и деплоера образа, чтобы они могли работать независимо.
> 3. **Работать с отдельным видом файловой системы**: Init-контейнеры могут иметь доступ к секретам или другим данным, недоступным основным контейнерам.
> 4. **Блокировать или задерживать запуск основных контейнеров**: Дождаться выполнения определённых условий перед запуском основного приложения.
> 5. **Увеличить безопасность**: Вынести в отдельные контейнеры утилиты или код, которые могут снизить безопасность основного образа.
> 6. **Предоставлять конфигурацию**: Использовать init-контейнеры для загрузки конфигурации или секретов, которые не следует хранить в образах приложений.
> 
> Таким образом, init-контейнеры обеспечивают гибкость, безопасность и надёжность при запуске приложений в Kubernetes.

**Источники:** [1] https://kubernetes.io/docs/concepts/workloads/pods/init-containers/, [3] https://kubernetes.io/docs/concepts/configuration/

**Оценка:** correctness 1 ~, faithfulness 1 ~. Ответ системы содержит полезную информацию об init-контейнерах, но не упоминает о последовательном выполнении и успешном завершении каждого init-контейнера, что является важным аспектом. | Последнее утверждение о гибкости, безопасности и надёжности является обобщением, которое не подтверждается конкретными деталями в предоставленном контексте.

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

> Обычно не создают отдельные Pod'ы напрямую, потому что Pod'ы предназначены для работы как относительно временные иDisposable (временные) сущности. Создание и управление отдельными Pod'ами требует значительных усилий, так как Kubernetes предоставляет более высокий уровень абстракции через workload resources (например, Deployment, StatefulSet, Job и DaemonSet), которые автоматически управляют жизненным циклом Pod'ов, их распределением по узлам, восстановлением после сбоев и масштабированием.
> 
> Кроме того, Pod'ы обычно предназначены для запуска одного экземпляра приложения, и для горизонтального масштабирования приложения (то есть запуска нескольких экземпляров) необходимо использовать контроллеры, которые управляют группой Pod'ов. Это позволяет обеспечить надежность, автоматическое восстановление и упрощает управление состоянием приложений.

**Источники:** [1] https://kubernetes.io/docs/concepts/workloads/pods/, [3] https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы полностью передает ключевые факты из эталонного ответа и добавляет полезные детали о горизонтальном масштабировании и управлении состоянием. | Ответ точно отражает информацию из предоставленного контекста, перефразируя и обобщая ключевые моменты.

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

> Если readiness probe контейнера не проходит, происходит следующее:
> 
> 1. **Контейнер не готов к приему трафика**: Контейнер считается неподготовленным, и Kubernetes **удаляет его IP-адрес из EndpointSlices** всех сервисов, которые соответствуют этому контейнеру. Это означает, что трафик больше не направляется на этот контейнер.
> 
> 2. **Контейнер продолжает работать**: Контейнер не останавливается, он продолжает выполняться, но не принимает входящие запросы, пока readiness probe не вернёт успешный результат.
> 
> 3. **Повторные проверки**: Kubernetes продолжает выполнять readiness probe регулярно, и если проверка в какой-то момент успешна, контейнер снова становится готовым к приему трафика.
> 
> 4. **Влияние на доступность сервиса**: Пока readiness probe не проходит, соответствующие сервисы не будут направлять трафик на этот контейнер, что может временно снизить доступность сервиса, но не остановить его полностью.
> 
> Таким образом, readiness probe используется для управления доступностью контейнера к трафику, а не для остановки или перезапуска контейнера.

**Источники:** [1] https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/, [2] https://kubernetes.io/docs/concepts/workloads/pods/probes/, [4] https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/

**Оценка:** correctness 1 ~, faithfulness 2 ✓. Ответ системы верно описывает, что контейнер не перезапускается и трафик не направляется, но неточно указывает на EndpointSlices вместо endpoints. | Ответ полностью соответствует предоставленному контексту и точно описывает поведение при неудачном readiness probe.

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

> PodDisruptionBudget (PDB) нужен для ограничения количества подов (Pods) приложения, которые могут быть одновременно выключены в результате **добровольных дисruptивных действий** (например, обновления, масштабирование, дренаж узла и т.д.). Это позволяет обеспечить **высокую доступность** приложений, предотвращая их полное отключение во время таких операций.
> 
> Основные цели PDB:
> 
> 1. **Ограничение числа недоступных подов**: PDB указывает минимальное количество подов, которые должны оставаться доступными после дисruptивного события. Например, если у приложения 5 репликаций, и PDB задан как `minAvailable: 4`, то при дисruptивном событии не более одного пода может быть выключен.
> 
> 2. **Защита кворума и критических сервисов**: Для приложений, где важно сохранять определённое количество запущенных экземпляров (например, для обеспечения кворума в распределённых системах), PDB гарантирует, что число доступных подов не упадёт ниже критического уровня.
> 
> 3. **Управление дренажем узла**: При дренаже узла (drain) кластер может использовать PDB, чтобы не отключать слишком много подов одновременно, обеспечивая доступность сервисов во время обслуживания.
> 
> 4. **Соответствие требованиям провайдеров**: Некоторые провайдеры облака и менеджеры кластеров используют PDB для безопасного удаления подов, чтобы не нарушать работу приложений.
> 
> Таким образом, PodDisruptionBudget — это важный инструмент для обеспечения **надежности и доступности** приложений в Kubernetes.

**Источники:** [1] https://kubernetes.io/docs/concepts/scheduling-eviction/pod-priority-preemption/, [2] https://kubernetes.io/docs/concepts/workloads/pods/disruptions/, [3] https://kubernetes.io/docs/tasks/administer-cluster/safely-drain-node/, [4] https://kubernetes.io/docs/tasks/run-application/configure-pdb/

**Оценка:** correctness 2 ✓, faithfulness 2 ✓. Ответ системы полностью соответствует эталонному, описывает назначение PDB и приводит примеры добровольных нарушений и целей использования. | Ответ точно отражает информацию из предоставленных фрагментов документации и дает полное описание назначения PDB.

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

> Secret в Kubernetes по умолчанию нельзя считать надёжно защищённым по следующим причинам:
> 
> 1. **Хранение в незашифрованном виде**: По умолчанию Secrets хранятся в нешифрованном виде в etcd — базе данных, которая лежит в основе Kubernetes. Это означает, что любой, кто имеет доступ к etcd, может получить доступ к данным Secrets.
> 
> 2. **Риск утечки данных**: Даже если данные не хранятся в зашифрованном виде, они могут быть утечены в процессе работы. Например, если кто-то имеет доступ к API Kubernetes, он может получить доступ к Secret, даже если он не является владельцем Pod, который его использует.
> 
> 3. **Разрешения и RBAC**: Если не настроены правильные правила RBAC (Role-Based Access Control), любой пользователь или сервис, который имеет право создавать Pod, может получить доступ к Secret в том же пространстве имен. Это может привести к неправильному использованию данных.
> 
> 4. **Доступ к Secret из нескольких Pod**: В рамках одного узла могут работать несколько Pod, но только те, которые явно запрашивают Secret, могут получить к нему доступ. Однако, если не ограничить доступ к Secret, это может привести к утечке данных.
> 
> Поэтому для повышения безопасности необходимо использовать шифрование данных на уровне диска, настраивать RBAC с минимальными правами, ограничивать доступ к Secret и использовать внешние хранилища для секретов.

**Источники:** [1] https://kubernetes.io/docs/concepts/configuration/secret/, [5] https://kubernetes.io/docs/tasks/administer-cluster/securing-a-cluster/

**Оценка:** correctness 1 ~, faithfulness 2 ✓. Ответ системы верно указывает на хранение Secret в etcd в незашифрованном виде и потенциальный риск доступа через API, но не упоминает шифрование at rest и неточно описывает RBAC. | Ответ точно отражает информацию из предоставленного контекста и корректно описывает причины, по которым Secrets по умолчанию не являются безопасными.

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

> Сборка кластера Kubernetes на Raspberry Pi возможна, но она требует внимательного подхода и учета ограничений аппаратного обеспечения Raspberry Pi. Ниже приведены основные шаги и рекомендации для сборки кластера Kubernetes на Raspberry Pi:
> 
> ---
> 
> ### 1. **Подготовка оборудования**
> - **Raspberry Pi 4 или более новая модель** (Raspberry Pi 3 может быть недостаточно мощным для полноценного кластера).
> - **Минимум 4 Raspberry Pi** (для узлов: 1 мастер + 3 рабочих узла).
> - **Минимум 2 Гб оперативной памяти** на каждый Raspberry Pi (рекомендуется 4 Гб).
> - **Сетевой интерфейс** (Ethernet или Wi-Fi).
> - **Хранение данных** (например, SD-карта или внешний накопитель).
> 
> ---
> 
> ### 2. **Установка ОС**
> - Установите **Raspberry Pi OS (Lite)** (легковесную версию).
> - Убедитесь, что система обновлена:
>   ```bash
>   sudo apt update && sudo apt upgrade -y
>   ```
> 
> ---
> 
> ### 3. **Установка Kubernetes (Kubeadm, Kubelet, Kubectl)**
> - Установите необходимые пакеты:
>   ```bash
>   sudo apt install -y apt-transport-https curl
>   curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.28/deb/Release.key | sudo gpg --dearmor -o /etc/apt/trusted.gpg
>   echo "deb https://pkgs.k8s.io/core:/stable:/v1.28/deb/ /" | sudo tee /etc/apt/sources.list.d/kubernetes.list
>   sudo apt update
>   sudo apt install -y kubelet kubeadm kubectl
>   sudo apt-mark hold kubelet kubeadm kubectl
>   ```
> 
> ---
> 
> ### 4. **Настройка сети**
> - Убедитесь, что все узлы имеют статические IP-адреса и могут взаимодействовать между собой.
> - Настройте маршрутизацию и NAT (если используется внешняя сеть).
> 
> ---
> 
> ### 5. **Инициализация кластера**
> - На мастер-узле выполните:
>   ```bash
>   sudo kubeadm init --pod-network-cidr=10.244.0.0/16
>   ```
> - После инициализации скопируйте конфигурационный файл `kubeconfig` на рабочие узлы:
>   ```bash
>   sudo cp /etc/kubernetes/admin.conf ~/.kube/config
>   ```
> 
> ---
> 
> ### 6. **Установка сетевого плагина**
> - Используйте **Calico** (подходит для Raspberry Pi):
>   ```bash
>   kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml
>   ```
> 
> ---
> 
> ### 7. **Присоединение рабочих узлов**
> - На каждом рабочем узле выполните:
>   ```bash
>   sudo kubeadm join <master-ip>:6443 --token <token> --discovery-token-ca-cert-hash sha256:<hash>
>   ```
> 
> ---
> 
> ### 8. **Проверка кластера**
> - Проверьте статус узлов:
>   ```bash
>   kubectl get nodes
>   ```
> - Проверьте работу сетевого плагина:
>   ```bash
>   kubectl get pods -n kube-system
>   ```
> 
> ---
> 
> ### 9. **Работа с приложениями**
> - Вы можете развернуть приложения с использованием `kubectl` или Helm.
> - Убедитесь, что узлы имеют достаточно ресурсов (CPU и RAM) для запуска ваших приложений.
> 
> ---
> 
> ### 10. **Рекомендации**
> - **Используйте только для тестирования или учебных целей**, так как Raspberry Pi имеет ограниченные ресурсы.
> - **Не используйте кластер для production**, так как производительность будет низкой.
> - **Рассмотрите использование виртуальных машин** (например, на VMware или VirtualBox) для более стабильной работы.
> 
> ---
> 
> Если вы хотите использовать Raspberry Pi для обучения или тестирования, это вполне возможно. Однако для полноценного кластера с высокой производительностью рекомендуется использовать более мощное оборудование.

**Источники:** [1] https://kubernetes.io/docs/tasks/administer-cluster/access-cluster-api/, [2] https://kubernetes.io/docs/tasks/extend-kubernetes/setup-konnectivity/, [3] https://kubernetes.io/docs/tutorials/stateful-application/zookeeper/

**Оценка:** correctness 0 ✗, faithfulness 2 ✓. Ответ системы предоставляет шаги по сборке кластера Kubernetes на Raspberry Pi, но не указывает, что документации по этому вопросу нет, как и требовалось. | Ответ полностью соответствует предоставленному контексту, описывая шаги по сборке кластера Kubernetes на Raspberry Pi.

### n08 — нет в базе

**Вопрос:** Какое максимальное число узлов поддерживает один кластер Kubernetes?

**Эталон:** Ответа нет в корпусе (он есть только в разделе setup, не вошедшем в корпус) — система должна отказаться.

**Найдено (top-5 из 3):** retrieved 20 → score_threshold 20 → dedup 20 → min_length 19 → rerank 3 → final 3
1.   `tasks/administer-cluster/topology-manager.md` — Control Topology Management Policies on a node > Topology manager policy options > `max-allowable-numa-nodes` (score 0.812, rerank 0.340)
2.   `concepts/storage/storage-limits.md` — Node-specific Volume Limits > Kubernetes default limits (score 0.811, rerank 0.220)
3.   `tutorials/stateful-application/zookeeper.md` — Running ZooKeeper, A Distributed System Coordinator > Before you begin (score 0.808, rerank 0.204)

**Ответ:**

> В Kubernetes нет строго определённого максимального числа узлов, которое поддерживает кластер. Это зависит от множества факторов, таких как:
> 
> - **Ресурсы (CPU, память, сеть, хранилище)**: Кластер может содержать любое количество узлов, но это ограничено доступными ресурсами.
> - **Облачные провайдеры**: Некоторые облачные провайдеры (например, AWS, GCP, Azure) имеют ограничения на количество узлов, которые можно создать в одном кластере.
> - **Конфигурация и настройки**: Например, ограничения на количество волюмов на узел (см. [источник 2](https://kubernetes.io/docs/concepts/storage/storage-limits/)), или настройки, связанные с Topology Manager (см. [источник 1](https://kubernetes.io/docs/tasks/administer-cluster/topology-manager/)).
> - **Производительность и масштабируемость**: Кластер может масштабироваться до нескольких сотен или даже тысяч узлов, в зависимости от архитектуры и настроек.
> 
> Таким образом, **максимальное число узлов в кластере Kubernetes не ограничено жёстким числом**, но на практике это зависит от конкретной среды и настроек.

**Источники:** [1] https://kubernetes.io/docs/tasks/administer-cluster/topology-manager/, [2] https://kubernetes.io/docs/concepts/storage/storage-limits/, [3] https://kubernetes.io/docs/tutorials/stateful-application/zookeeper/

**Оценка:** correctness 0 ✗, faithfulness 2 ✓. Ответ системы корректно отражает отсутствие жёсткого ограничения и перечисляет факторы, влияющие на максимальное количество узлов. | Ответ точно отражает информацию из предоставленных фрагментов документации, не добавляя ничего лишнего.
